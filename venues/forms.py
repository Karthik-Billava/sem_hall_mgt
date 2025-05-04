from django import forms
from .models import Venue, VenueImage
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class VenueForm(forms.ModelForm):
    """Form for venue creation and editing"""
    class Meta:
        model = Venue
        fields = [
            'name', 'description', 'address', 'city', 'state', 'zip_code',
            'capacity', 'hourly_rate', 'has_projector', 'has_sound_system',
            'has_wifi', 'has_catering', 'has_parking', 'has_air_conditioning'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_hourly_rate(self):
        hourly_rate = self.cleaned_data.get('hourly_rate')
        if hourly_rate <= 0:
            raise forms.ValidationError("Hourly rate must be greater than zero")
        return hourly_rate

class VenueImageForm(forms.ModelForm):
    """Form for venue images"""
    class Meta:
        model = VenueImage
        fields = ['image', 'is_primary', 'is_cover', 'caption']
        labels = {
            'is_primary': 'Set as primary image',
            'is_cover': 'Set as cover image',
        }
        help_texts = {
            'is_primary': 'This image will be the main image shown in listings',
            'is_cover': 'This image will be shown at the top of the venue detail page',
            'caption': 'Optional caption to describe this image',
        }

class VenueSearchForm(forms.Form):
    """Form for searching venues"""
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Search venues...',
        'class': 'form-control'
    }))
    min_capacity = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={
        'placeholder': 'Min capacity',
        'class': 'form-control',
        'min': '1'
    }))
    max_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={
        'placeholder': 'Max price per hour',
        'class': 'form-control',
        'min': '0',
        'step': '0.01'
    }))
    has_projector = forms.BooleanField(required=False)
    has_sound_system = forms.BooleanField(required=False)
    has_wifi = forms.BooleanField(required=False)
    has_catering = forms.BooleanField(required=False)
    has_parking = forms.BooleanField(required=False)
    has_air_conditioning = forms.BooleanField(required=False) 