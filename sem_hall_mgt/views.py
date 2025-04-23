from django.shortcuts import render
from venues.models import Venue

def home_view(request):
    """
    Home page view that displays the latest venues
    """
    # Get 5 most recently added venues that are active
    latest_venues = Venue.objects.filter(is_active=True).order_by('-created_at')[:5]
    
    context = {
        'latest_venues': latest_venues
    }
    
    return render(request, 'home.html', context) 