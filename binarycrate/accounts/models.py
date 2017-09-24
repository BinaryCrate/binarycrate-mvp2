from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    email = models.EmailField('email address', max_length=254, unique=True,
                              db_index=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Should not include USERNAME_FIELD

