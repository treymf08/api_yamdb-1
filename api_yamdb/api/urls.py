from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import create_user

urlpatterns = [
    path('v1/auth/signup/', create_user),
    path('v1/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]