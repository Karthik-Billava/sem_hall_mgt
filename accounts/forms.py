from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Review

class CustomSignupForm(forms.Form):
    """Custom fields for signup form"""
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    user_type = forms.ChoiceField(
        choices=UserProfile.USER_TYPES,
        required=True,
        initial='regular',
        help_text='Select "Venue Manager" if you want to list and manage venues.'
    )
    
    def signup(self, request, user):
        """Save the user's profile"""
        # Set first name and last name
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        
        # Update profile with user type
        profile = UserProfile.objects.get_or_create(user=user)[0]
        profile.user_type = self.cleaned_data['user_type']
        profile.save()

class UserProfileForm(forms.ModelForm):
    """Form for user profile"""
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    
    class Meta:
        model = UserProfile
        fields = ('phone_number', 'address', 'profile_picture', 'bio', 'date_of_birth')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name

class ReviewForm(forms.ModelForm):
    """Form for venue reviews"""
    class Meta:
        model = Review
        fields = ('rating', 'comment')
        widgets = {
            'rating': forms.RadioSelect(),
            'comment': forms.Textarea(attrs={
                'rows': 4, 
                'placeholder': 'Share your experience with this venue...',
                'class': 'form-control'
            }),
        }
        labels = {
            'rating': 'How would you rate this venue?',
            'comment': 'Your Review'
        }
        help_texts = {
            'rating': 'Select a rating from 1 to 5 stars',
        } 