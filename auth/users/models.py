from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=255, unique=True)
    username = None

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []