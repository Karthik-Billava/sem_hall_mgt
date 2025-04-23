from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile
from notifications_app.models import NotificationSetting

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a user profile when a new user is created"""
    if created:
        UserProfile.objects.create(user=instance)
        NotificationSetting.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the user profile when the user is saved"""
    # Check if profile exists before saving
    try:
        if hasattr(instance, 'profile'):
            instance.profile.save()
    except Exception:
        # If profile doesn't exist, create it
        UserProfile.objects.get_or_create(user=instance)
    
    # Create notification settings if they don't exist
    try:
        if hasattr(instance, 'notification_settings'):
            instance.notification_settings
        else:
            NotificationSetting.objects.get_or_create(user=instance)
    except NotificationSetting.DoesNotExist:
        NotificationSetting.objects.create(user=instance) 