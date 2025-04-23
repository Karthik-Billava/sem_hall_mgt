from django.db import models
from django.contrib.auth.models import User

class NotificationSetting(models.Model):
    """Model for user notification preferences"""
    NOTIFICATION_TYPES = (
        ('email', 'Email Notifications'),
        ('sms', 'SMS Notifications'),
        ('push', 'Push Notifications'),
        ('in_app', 'In-App Notifications'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_settings')
    booking_updates = models.BooleanField(default=True)
    reviews = models.BooleanField(default=True)
    promotions = models.BooleanField(default=False)
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    push_notifications = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Notification settings for {self.user.username}" 