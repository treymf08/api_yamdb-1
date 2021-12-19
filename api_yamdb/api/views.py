from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.base_user import BaseUserManager
from django.core.mail import EmailMessage
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, serializers, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend

from reviews.models import Category, Genre, Review, Title
from users.models import User
from .filters import TitleFilter
from .permissions import CommentReviewPermission, IsAdmin, IsAdminOrReadOnly
from .serializers import (
    CategorySerializer, CommentSerializer, CreateUserSerializer,
    GenreSerializer, ReviewSerializer, UsersSerializer, TitleSerializer,
    TokenSerializer)

BAD_CONFIRMATION_CODE = 'Это поле некорректно'
MAIL_SUBJECT = 'Ваш confirmation code'


@api_view(['POST'])
def create_user(request):
    """Создаёт нового или получает из базы ранее созданного пользователя и
       высылает код для получения токена на почту.
    """
    serializer = CreateUserSerializer(data=request.data)
    email = serializer.initial_data.get('email', None)
    username = serializer.initial_data.get('username', None)
    if (serializer.is_valid() or User.objects.filter(username=username,
                                                     email=email).exists()):
        user, created = User.objects.get_or_create(
            email=email, username=username)
        user.set_password(BaseUserManager().make_random_password())
        user.save()
        current_site = get_current_site(request).domain
        email_for_user = EmailMessage(MAIL_SUBJECT, user.password,
                                      current_site, [email])
        email_for_user.send()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_token(request):
    """Создаёт токен для пользователя."""
    serializer = TokenSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    username = serializer.data['username']
    user = get_object_or_404(User, username=username)
    confirmation_code = serializer.data['confirmation_code']
    if confirmation_code == user.password:
        token = RefreshToken.for_user(user).access_token
        data = {'token': str(token)}
        return Response(data, status=status.HTTP_200_OK)
    data = {'confirmation_code': BAD_CONFIRMATION_CODE}
    return Response(data, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для модели User."""
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = [IsAdmin]
    pagination_class = PageNumberPagination
    lookup_field = 'username'


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def myself(request):
    """Позволяет пользователю получить или изменить информацию о себе."""
    user = request.user
    if request.method == 'GET':
        serializer = UsersSerializer(user)
        return Response(serializer.data)
    serializer = UsersSerializer(user, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    if user.role != 'admin':
        serializer.save(role=user.role)
    else:
        serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


class CreateListDestroy(mixins.CreateModelMixin, mixins.ListModelMixin,
                        mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """Класс для получения списка объектов, создания или удаления объекта."""
    pass


class CategoryViewSet(CreateListDestroy):
    """ViewSet для модели Category."""
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    pagination_class = PageNumberPagination
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'


class GenreViewSet(CreateListDestroy):
    """ViewSet для модели Genre."""
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    pagination_class = PageNumberPagination
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Title."""
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    pagination_class = PageNumberPagination
    serializer_class = TitleSerializer
    queryset = Title.objects.all()
    permission_classes = [IsAdminOrReadOnly]

    def get_category_genres(self, serializer):
        category_slug = serializer.initial_data.get('category')
        category = get_object_or_404(Category, slug=category_slug)
        genre_slugs = serializer.initial_data.getlist('genre')
        genres = []
        for slug in genre_slugs:
            genre = get_object_or_404(Genre, slug=slug)
            genres.append(genre)
        serializer.save(category=category, genre=genres)

    def perform_create(self, serializer):
        self.get_category_genres(serializer)

    def perform_update(self, serializer):
        self.get_category_genres(serializer)


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Review."""
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination
    permission_classes = [CommentReviewPermission]

    def update_rating(self, title):
        reviews = title.reviews.all()
        sums = reviews.aggregate(Avg("score"))
        title.rating = int(sums['score__avg'])
        title.save()

    def get_title(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        return title

    def perform_update(self, serializer):
        title = self.get_title()
        serializer.save()
        self.update_rating(title)

    def perform_destroy(self, instance):
        title = self.get_title()
        instance.delete()
        self.update_rating(title)

    def perform_create(self, serializer):
        title = self.get_title()
        author = self.request.user
        if Review.objects.filter(author=author, title=title).exists():
            raise serializers.ValidationError()
        serializer.save(author=self.request.user, title=title)
        self.update_rating(title)

    def get_queryset(self):
        title = self.get_title()
        return title.reviews.all()


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Comment."""
    serializer_class = CommentSerializer
    pagination_class = PageNumberPagination
    permission_classes = [CommentReviewPermission]

    def get_review(self):
        review_id = self.kwargs.get('review_id')
        return get_object_or_404(Review, id=review_id)

    def perform_create(self, serializer):
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)

    def get_queryset(self):
        review = self.get_review()
        return review.comments.all()
