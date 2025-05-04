from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid

class Venue(models.Model):
    """Model for seminar halls/venues"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    capacity = models.PositiveIntegerField()
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managed_venues')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Amenities
    has_projector = models.BooleanField(default=False)
    has_sound_system = models.BooleanField(default=False)
    has_wifi = models.BooleanField(default=False)
    has_catering = models.BooleanField(default=False)
    has_parking = models.BooleanField(default=False)
    has_air_conditioning = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    
    def get_average_rating(self):
        """Calculate the average rating for this venue"""
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0
    
    def get_amenities(self):
        """Get a list of available amenities"""
        amenities = []
        if self.has_projector:
            amenities.append('Projector')
        if self.has_sound_system:
            amenities.append('Sound System')
        if self.has_wifi:
            amenities.append('WiFi')
        if self.has_catering:
            amenities.append('Catering')
        if self.has_parking:
            amenities.append('Parking')
        if self.has_air_conditioning:
            amenities.append('Air Conditioning')
        return amenities
    
    def get_cover_image(self):
        """Get the cover image for this venue"""
        cover_image = self.images.filter(is_cover=True).first()
        if cover_image:
            return cover_image
        # Fall back to primary image if no cover image
        primary_image = self.images.filter(is_primary=True).first()
        if primary_image:
            return primary_image
        # Fall back to first image if no primary image
        return self.images.first()
    
    def get_upcoming_bookings(self, days=30):
        """Get upcoming bookings for this venue"""
        today = timezone.now().date()
        end_date = today + timezone.timedelta(days=days)
        return self.bookings.filter(
            date__gte=today,
            date__lte=end_date,
            status__in=['pending', 'approved']
        ).order_by('date', 'start_time')

class VenueImage(models.Model):
    """Model for venue images"""
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='venue_images/')
    is_primary = models.BooleanField(default=False)
    is_cover = models.BooleanField(default=False, help_text="Designate this image as the cover image (shown at the top of venue detail page)")
    caption = models.CharField(max_length=255, blank=True, help_text="Optional caption for the image")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image for {self.venue.name}"
    
    def save(self, *args, **kwargs):
        """Override save to handle is_primary and is_cover flags"""
        if self.is_primary:
            # Set other images for this venue as not primary
            VenueImage.objects.filter(venue=self.venue, is_primary=True).update(is_primary=False)
        
        if self.is_cover:
            # Set other images for this venue as not cover
            VenueImage.objects.filter(venue=self.venue, is_cover=True).update(is_cover=False)
        
        super().save(*args, **kwargs) 