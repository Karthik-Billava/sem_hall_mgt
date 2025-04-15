from django.db import models
from phonenumber_field.modelfields import PhoneNumberField 

from login.models import CustomUser


# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    phone_number = PhoneNumberField(blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    user_type = models.CharField(max_length=20, choices=CustomUser.USER_TYPES, default='regular')
    bio = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)