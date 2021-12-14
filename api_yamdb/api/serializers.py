from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.models import User

CHANGE_USERNAME = 'Нельзя создать пользователя с username = "me"'


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())])

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(CHANGE_USERNAME)
        return value


class UserFullSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
