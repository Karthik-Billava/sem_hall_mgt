from django import forms
from .models import NotificationSetting

class NotificationSettingForm(forms.ModelForm):
    """Form for notification settings"""
    class Meta:
        model = NotificationSetting
        fields = [
            'booking_updates', 
            'reviews', 
            'promotions',
            'email_notifications',
            'sms_notifications',
            'push_notifications'
        ]
        widgets = {
            'booking_updates': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'reviews': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'promotions': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sms_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'push_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        } 