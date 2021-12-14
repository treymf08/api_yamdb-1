from rest_framework import serializers
<<<<<<< HEAD

from reviews.models import Review, Comment


class ReviewSerializer(serializers.ModelSerializer):
    # author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = '__all__'
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = '__all__'
        model = Comment
=======
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
>>>>>>> master
