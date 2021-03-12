from django.db import models

# Create your models here.
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.db import models
from rest_framework.authtoken.models import Token

class CustomUserManager(BaseUserManager):

    def create_user(self, username, email, password=None, address=None, **kw_args):
        if not username:
            raise TypeError('Users should have a username')
        if not email:
            raise TypeError('Users should have an Email')

        user = self.model(username=username,
                          email=self.normalize_email(email),
                          address=address
                          )
        user.set_password(password)

        user.save()
        Token.objects.create(user=user)
        return user

    def create_superuser(self, username, email, password=None):
        if password in None:
            raise TypeError('Password should not be none')

        user = self.create_user(username=username,
                                email=self.normalize_email(email),
                                password=password)

        user.is_super = True
        user.is_staff = True
        user.save()
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50, unique=True, db_index=True)
    email = models.EmailField(max_length=50, unique=True)
    address = models.CharField(max_length=255, null=True)
    is_active = models.BooleanField(default=True) # byDefault True
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    def __str__(self):
        return f'{self.email} - {self.username} - {self.address}'