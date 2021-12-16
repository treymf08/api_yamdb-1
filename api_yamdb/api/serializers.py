from rest_framework import serializers

from users.models import User

CHANGE_USERNAME = 'Нельзя создать пользователя с username = "me"'


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(CHANGE_USERNAME)
        return value


class UsersSerializer(CreateUserSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')



class CategorySerializer(serializers.ModelSerializer):

    #class Meta:
    #   model = Category
    #   fields = ('name', 'slug')
    pass


class GenreSerializer(serializers.ModelSerializer):

    #class Meta:
    #   model = Genre
    #   fields = ('name', 'slug')

    pass


class TitleSerializer(serializers.ModelSerializer):

    pass

class TokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()

