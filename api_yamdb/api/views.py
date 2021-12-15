from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.base_user import BaseUserManager
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken


from users.models import User
from .permissions import IsAdmin
from .serializers import CreateUserSerializer, UsersSerializer, TokenSerializer


@api_view(['POST'])
def create_user(request):
    serializer = CreateUserSerializer(data=request.data)
    if serializer.is_valid():
        password = BaseUserManager().make_random_password()
        serializer.save(password=password)
        user_email = serializer.data['email']
        subject = 'Your confirmation code'
        current_site = get_current_site(request).domain
        confirmation_code = password
        email = EmailMessage(subject, confirmation_code,
                             current_site, [user_email])
        email.send()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def token_create(request):
    serializer = TokenSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.data['username']
        user = get_object_or_404(User, username=username)
        confirmation_code = serializer.data['confirmation_code']
        if confirmation_code == user.password:
            token = RefreshToken.for_user(user).access_token
            data = {'token': str(token)}
            return Response(data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = [IsAdmin]
    pagination_class = PageNumberPagination


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def myself(request):
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


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAdmin])
def admin_get_user(request, username):
    user = get_object_or_404(User, username=username)
    if request.method == 'GET':
        serializer = UsersSerializer(user)
        return Response(serializer.data)
    if request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    serializer = UsersSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
