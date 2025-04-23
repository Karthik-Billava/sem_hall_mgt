from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Review

class CustomUserCreationForm(UserCreationForm):
    """Custom user registration form"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    """Form for user profile"""
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    
    class Meta:
        model = UserProfile
        fields = ('phone_number', 'address', 'profile_picture', 'bio', 'date_of_birth', 'user_type')
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