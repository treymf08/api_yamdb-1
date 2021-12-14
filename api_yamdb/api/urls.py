from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import routers


from .views import create_user, myself, admin_get_user, UserViewSet

router = routers.DefaultRouter()
router.register('users', UserViewSet)


urlpatterns = [
    path('v1/users/me/', myself),
    path('v1/users/<str:username>/', admin_get_user),
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', create_user),
    path('v1/auth/token/', TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
]
