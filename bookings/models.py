from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from venues.models import Venue
import uuid

class Booking(models.Model):
    """Model for venue bookings"""
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    
    booking_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='bookings')
    event_name = models.CharField(max_length=100)
    event_description = models.TextField()
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    attendees = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approval_time = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-date', '-start_time']
    
    def __str__(self):
        return f"{self.event_name} at {self.venue.name} on {self.date}"
    
    def is_past(self):
        """Check if this booking is in the past"""
        now = timezone.now()
        booking_datetime = timezone.make_aware(
            timezone.datetime.combine(self.date, self.end_time)
        )
        return booking_datetime < now
    
    def is_upcoming(self):
        """Check if this booking is upcoming"""
        now = timezone.now()
        booking_datetime = timezone.make_aware(
            timezone.datetime.combine(self.date, self.start_time)
        )
        return booking_datetime > now
    
    def get_payment_deadline(self):
        """Get the payment deadline (24 hours after approval)"""
        if self.approval_time:
            return self.approval_time + timezone.timedelta(hours=24)
        return None
    
    def get_remaining_payment_time(self):
        """Get remaining time for payment in seconds"""
        if self.status != 'approved' or not self.approval_time:
            return 0
            
        # If payment already exists, return 0
        try:
            if self.payment and self.payment.status == 'completed':
                return 0
        except:
            pass
            
        now = timezone.now()
        deadline = self.get_payment_deadline()
        
        if now >= deadline:
            return 0
            
        time_remaining = deadline - now
        return time_remaining.total_seconds()
        
    def is_payment_deadline_passed(self):
        """Check if payment deadline has passed"""
        if self.approval_time:
            now = timezone.now()
            deadline = self.get_payment_deadline()
            return now > deadline
        return False

class Payment(models.Model):
    """Model for booking payments"""
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('paypal', 'PayPal'),
        ('cash', 'Cash'),
    )
    
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Payment for {self.booking.event_name} - {self.status}" 