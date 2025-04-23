from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile
from notifications_app.models import NotificationSetting


class Command(BaseCommand):
    help = 'Creates missing user profiles and notification settings'

    def handle(self, *args, **options):
        # Get all users
        users = User.objects.all()
        profiles_created = 0
        notification_settings_created = 0

        # Check each user
        for user in users:
            # Create UserProfile if missing
            try:
                user.profile
            except User.profile.RelatedObjectDoesNotExist:
                UserProfile.objects.create(user=user)
                profiles_created += 1
                self.stdout.write(self.style.SUCCESS(f'Created profile for user: {user.username}'))

            # Create NotificationSetting if missing
            try:
                user.notification_settings
            except:
                NotificationSetting.objects.create(user=user)
                notification_settings_created += 1
                self.stdout.write(self.style.SUCCESS(f'Created notification settings for user: {user.username}'))

        self.stdout.write(self.style.SUCCESS(
            f'Command complete. Created {profiles_created} profiles and {notification_settings_created} notification settings.')) 