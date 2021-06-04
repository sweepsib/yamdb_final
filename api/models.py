from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .managers import UserManager
from .validators import year_validator


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = 'user'
        MODERATOR = 'moderator'
        ADMIN = 'admin'
        DJANGO_ADMIN = 'django_admin'

    email = models.EmailField(verbose_name='email', unique=True)
    role = models.TextField(
        verbose_name='role',
        choices=Role.choices,
        default='user'
    )
    bio = models.TextField(verbose_name='about', null=True)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        ordering = ['-id']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_moderator(self):
        return self.role == self.Role.MODERATOR

    @property
    def is_staff(self):
        return self.is_admin or self.is_moderator


class Genre(models.Model):
    name = models.CharField(verbose_name='genre', max_length=30)
    slug = models.SlugField(verbose_name='slug', unique=True)

    class Meta:
        ordering = ['-id']
        verbose_name = 'Genre'
        verbose_name_plural = 'Genres'

    def __str__(self):
        return self.slug


class Category(models.Model):
    name = models.CharField(verbose_name='category', max_length=50)
    slug = models.SlugField(verbose_name='slug', unique=True)

    class Meta:
        ordering = ['-id']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.slug


class Title(models.Model):
    name = models.CharField(verbose_name='name', max_length=200)
    year = models.IntegerField(
        verbose_name='release date',
        validators=[year_validator]
    )
    category = models.ForeignKey(
        Category,
        verbose_name='category',
        on_delete=models.SET_NULL,
        related_name='titles',
        null=True,
        blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='genre',
        related_name='titles'
    )
    description = models.TextField(
        verbose_name='description',
        blank=True,
        null=True
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Title'
        verbose_name_plural = 'Titles'

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='title',
        related_name='reviews',
        blank=True,
        null=True
    )
    text = models.CharField(max_length=200, verbose_name='Text', )
    score = models.IntegerField(
        verbose_name='rating',
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='publication date',
        db_index=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='author',
        related_name='reviews',
        blank=True,
        null=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'review'
        verbose_name_plural = 'Reviews'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review',
            )
        ]

    def __str__(self):
        return self.text[:20]


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.SET_NULL,
        verbose_name='review',
        related_name='comments',
        blank=True,
        null=True
    )
    text = models.CharField(
        max_length=200,
        verbose_name='text'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='author',
        related_name='comments',
        blank=True,
        null=True
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='publication date',
        db_index=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

    def __str__(self):
        return self.text[:20]
