from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLES = [('user', 'Аутентифицированный пользователь'),
             ('moderator', 'Модератор'), ('admin', 'Администратор')]

    email = models.EmailField('Почта', unique=True)
    bio = models.TextField('Биография', blank=True,)
    role = models.CharField('Роль', max_length=50,
                            choices=ROLES, default='user')
