from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    def _create_user(
        self, email, password, first_name, last_name, about_self, **extra_fields
    ):
        if not email:
            raise ValueError("You must write your email")
        if not password:
            raise ValueError("Password must be provided")

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            about_self=about_self,
            **extra_fields
        )

        user.set_password(password)
        user.save()
        return user

    def create_user(
        self,
        email=None,
        password=None,
        first_name=None,
        last_name=None,
        about_self=None,
        **extra_fields
    ):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(
            email, password, first_name, last_name, about_self, **extra_fields
        )

    def create_superuser(
        self,
        email=None,
        password=None,
        first_name="Default",
        last_name="Superuser",
        about_self=None,
        **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self._create_user(
            email, password, first_name, last_name, about_self, **extra_fields
        )


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=250, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=120)
    about_self = models.CharField(max_length=500, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
