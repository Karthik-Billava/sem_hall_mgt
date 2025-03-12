from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class CustomUser(AbstractUser):
    USER_TYPES = (
        ('regular', 'Regular User'),
        ('venue_manager', 'Venue Manager'),
    )
    user_type = models.CharField(
        max_length=15, choices=USER_TYPES, default='regular')

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
