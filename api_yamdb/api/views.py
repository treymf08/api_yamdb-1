from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail, EmailMessage
from django.contrib.sites.shortcuts import get_current_site


from users.models import User
from .permissions import IsAdmin
from .serializers import UserSerializer, UserFullSerializer


@api_view(['POST'])
def create_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        subject = 'Your confirmation code'
        current_site = get_current_site(request).domain
        user_email = serializer.data['email']
        confirmation_code = 'code'
        email = EmailMessage(subject, confirmation_code,
                             current_site, [user_email])
        email.send()

        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserFullSerializer
    permission_classes = [IsAdmin]
    pagination_class = PageNumberPagination


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def myself(request):
    user = request.user
    if request.method == 'PATCH':
        serializer = UserFullSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            if user.role != 'admin':
                serializer.save(role=user.role)
            else:
                serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    serializer = UserFullSerializer(user)
    return Response(serializer.data)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAdmin])
def admin_get_user(request, username):
    user = get_object_or_404(User, username=username)
    if request.method == 'PATCH':
        serializer = UserFullSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    serializer = UserFullSerializer(user)
    return Response(serializer.data)
