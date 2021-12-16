from django.contrib import admin

from .models import Category, Genre, Title, Review, Comment

admin.site.register([Category, Genre, Title, Review, Comment])
