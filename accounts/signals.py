from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile
from notifications_app.models import NotificationSetting

@receiver(post_save, sender=User)
def handle_user_save(sender, instance, created, **kwargs):
    """Handle user creation and updates"""
    # Create or get user profile
    if not hasattr(instance, 'profile'):
        UserProfile.objects.create(user=instance)
    
    # Create or get notification settings
    NotificationSetting.objects.get_or_create(user=instance) 