from django import forms
from .models import Booking, Payment
from datetime import datetime, timedelta

class BookingForm(forms.ModelForm):
    """Form for venue booking"""
    class Meta:
        model = Booking
        fields = ['event_name', 'event_description', 'date', 'start_time', 'end_time', 'attendees']
        widgets = {
            'event_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter event name'}),
            'event_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe your event'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'min': datetime.now().date().isoformat()}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'attendees': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }
    
    def clean(self):
        """Validate booking form data"""
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        # Check if date is in the past
        if date and date < datetime.now().date():
            self.add_error('date', 'Booking date cannot be in the past.')
        
        # Check if end time is after start time
        if start_time and end_time and start_time >= end_time:
            self.add_error('end_time', 'End time must be after start time.')
        
        # Check if booking is at least 1 hour
        if start_time and end_time:
            duration = (datetime.combine(datetime.today(), end_time) - 
                       datetime.combine(datetime.today(), start_time)).seconds / 3600
            if duration < 1:
                self.add_error('end_time', 'Booking must be at least 1 hour.')
        
        return cleaned_data

class PaymentForm(forms.ModelForm):
    """Form for booking payment"""
    class Meta:
        model = Payment
        fields = ['payment_method']
        
    # Add card details fields (these would not be saved to the database in a real app)
    card_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '1234 5678 9012 3456'})
    )
    card_expiry = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'MM/YY'})
    )
    card_cvv = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'CVV'})
    )
    
    def clean(self):
        """Validate payment form data"""
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        
        # Validate card details if payment method is credit/debit card
        if payment_method in ['credit_card', 'debit_card']:
            card_number = cleaned_data.get('card_number')
            card_expiry = cleaned_data.get('card_expiry')
            card_cvv = cleaned_data.get('card_cvv')
            
            if not card_number:
                self.add_error('card_number', 'Card number is required.')
            if not card_expiry:
                self.add_error('card_expiry', 'Card expiry date is required.')
            if not card_cvv:
                self.add_error('card_cvv', 'CVV is required.')
        
        return cleaned_data 