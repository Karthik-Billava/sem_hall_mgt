from django.db.models.signals import post_save
from django.dispatch import receiver
from login.models import CustomUser
from .models import UserProfile

@receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        UserProfile.objects.get_or_create(user=instance) 