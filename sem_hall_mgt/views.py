from django.shortcuts import render
from venues.models import Venue
from django.db.models import Count
from bookings.models import Booking

def home_view(request):
    """
    Home page view that displays the latest venues and most booked venues
    """
    # Get 5 most recently added venues that are active
    latest_venues = Venue.objects.filter(is_active=True).order_by('-created_at')[:5]
    
    # Get popular venues based on booking count
    popular_venues = Venue.objects.filter(is_active=True).annotate(
        booking_count=Count('bookings')
    ).order_by('-booking_count')[:5]
    
    context = {
        'latest_venues': latest_venues,
        'popular_venues': popular_venues
    }
    
    return render(request, 'home.html', context) 