from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLES = [('user', 'Аутентифицированный пользователь'),
             ('moderator', 'Модератор'), ('admin', 'Администратор')]

    email = models.EmailField('Почта', unique=True)
    bio = models.TextField('Биография', blank=True,)
    role = models.CharField('Роль', max_length=50,
                            choices=ROLES, default='user')


class Review(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    # score = # как выстовлять оценки?
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews')

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)
