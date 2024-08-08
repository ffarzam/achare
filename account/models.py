from django.contrib.auth.models import AbstractUser
from django.db import models

from account.manager import CustomManager
from account.utils import phone_number_regex

# Create your models here.


class User(AbstractUser):
    username = None
    phone = models.CharField(validators=[phone_number_regex], unique=True)
    is_active = models.BooleanField("active", default=False)

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    objects = CustomManager()
