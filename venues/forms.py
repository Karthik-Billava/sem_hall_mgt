from django import forms
from .models import Venue, VenueImage, Availability

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
            'description': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'hourly_rate': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
        }

class VenueImageForm(forms.ModelForm):
    """Form for venue images"""
    class Meta:
        model = VenueImage
        fields = ['image', 'caption', 'is_primary', 'is_cover']
        help_texts = {
            'is_primary': 'Set as the main thumbnail image for venue listings',
            'is_cover': 'Set as the cover image shown at the top of the venue detail page',
            'caption': 'Add a short description for this image (optional)',
        }
        widgets = {
            'caption': forms.TextInput(attrs={'placeholder': 'E.g., "Main hall with projector setup"'}),
        }

class AvailabilityForm(forms.ModelForm):
    """Form for venue availability"""
    class Meta:
        model = Availability
        fields = ['date', 'start_time', 'end_time', 'is_available']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }
    
    def clean(self):
        """Validate that end time is after start time"""
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("End time must be after start time.")
        
        return cleaned_data

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