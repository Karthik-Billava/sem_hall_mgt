from django import forms
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('first_name', 'last_name', 'phone_number', 'address', 'profile_picture', 'bio', 'date_of_birth')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'user_type': 'Account Type',
        }
        help_texts = {
            'user_type': 'Select "Venue Manager" if you want to list and manage venues.',
        }