from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from decimal import Decimal

class UserManager(BaseUserManager):
    def _create_user(self, email, password,
                     first_name, last_name,
                     profile_picture, about_self,
                     categories_liked, balance,
                     **extra_fields):
        if not email:
            raise ValueError('You must write your email')
        if not password:
            raise ValueError('Password must be provided')
        
        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            profile_picture=profile_picture,
            about_self=about_self,
            categories_liked=categories_liked,
            balance=balance,
            **extra_fields
        )

        user.set_password(password)
        user.save()
        return user

    def create_user(self, email=None, password=None, first_name=None, last_name=None,
                    profile_picture=None, about_self=None, categories_liked=None,
                    balance=Decimal('0.00'), **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, first_name, last_name,
                                 profile_picture, about_self, categories_liked,
                                 balance, **extra_fields)

    def create_superuser(self, email=None, password=None, first_name=None, last_name=None,
                         profile_picture=None, about_self=None, categories_liked=None,
                         balance=Decimal('0.00'), **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self._create_user(email, password, first_name, last_name,
                                 profile_picture, about_self, categories_liked,
                                 balance, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=250, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=120)
    profile_picture = models.ImageField(upload_to='users/%Y/%m/%d/', blank=True, null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    about_self = models.CharField(max_length=500, blank=True, null=True)
    categories_liked = models.JSONField(default=list)
    date_joined = models.DateTimeField(auto_now_add=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class Chat(models.Model):
    users = models.ManyToManyField(User, related_name='chats')

    def __str__(self):
        return 'Chat'


class Message(models.Model):
    chat = models.ForeignKey(Chat,
                             on_delete=models.CASCADE,
                             related_name='messages')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='messages')
    created = models.DateTimeField(auto_now_add=True)
    text = models.TextField()