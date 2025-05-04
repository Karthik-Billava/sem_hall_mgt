from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Venue, VenueImage
from .forms import VenueForm, VenueImageForm
from accounts.models import Review
from bookings.models import Booking
from datetime import datetime, timedelta
from functools import wraps
from django.utils.decorators import method_decorator
from django.utils import timezone

def venue_manager_required(view_func):
    """Decorator to check if user is a venue manager"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to access this page.')
            return redirect('account_login')
            
        if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'venue_manager':
            messages.error(request, 'You must be a venue manager to access this page.')
            return redirect('home')
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def venue_list(request):
    """View for listing all venues with search and filter functionality"""
    venues = Venue.objects.filter(is_active=True)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        venues = venues.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(state__icontains=search_query)
        )
    
    # Filter by capacity
    min_capacity = request.GET.get('min_capacity')
    if min_capacity:
        venues = venues.filter(capacity__gte=min_capacity)
    
    # Filter by price
    max_price = request.GET.get('max_price')
    if max_price:
        venues = venues.filter(hourly_rate__lte=max_price)
    
    # Filter by amenities
    if request.GET.get('has_projector'):
        venues = venues.filter(has_projector=True)
    if request.GET.get('has_sound_system'):
        venues = venues.filter(has_sound_system=True)
    if request.GET.get('has_wifi'):
        venues = venues.filter(has_wifi=True)
    if request.GET.get('has_catering'):
        venues = venues.filter(has_catering=True)
    if request.GET.get('has_parking'):
        venues = venues.filter(has_parking=True)
    if request.GET.get('has_air_conditioning'):
        venues = venues.filter(has_air_conditioning=True)
    
    # Pagination
    paginator = Paginator(venues, 9)  # Show 9 venues per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'min_capacity': min_capacity,
        'max_price': max_price,
    }
    return render(request, 'venues/venue_list.html', context)

def venue_detail(request, venue_id):
    """View for venue details"""
    venue = get_object_or_404(Venue, id=venue_id, is_active=True)
    reviews = Review.objects.filter(venue=venue).order_by('-created_at')
    
    # Get future dates for the next 30 days
    today = timezone.now().date()
    thirty_days_later = today + timedelta(days=30)
    
    # Get bookings for the next 30 days
    bookings = Booking.objects.filter(
        venue=venue,
        date__gte=today,
        date__lte=thirty_days_later,
        status__in=['pending', 'approved']
    ).select_related('payment').order_by('date', 'start_time')
    
    # Group bookings by date for display
    booking_dates = {}
    for booking in bookings:
        date_str = booking.date.strftime('%Y-%m-%d')
        
        # Check if booking has a completed payment
        has_payment = False
        try:
            has_payment = booking.payment and booking.payment.status == 'completed'
        except:
            pass
            
        if date_str not in booking_dates:
            booking_dates[date_str] = {
                'bookings': [],
                'has_confirmed_booking': False,
                'time_slots_available': True,
                'is_fully_booked': False  # New flag to track if date is fully booked
            }
            
        # Add booking info to the date
        booking_dates[date_str]['bookings'].append({
            'start_time': booking.start_time,
            'end_time': booking.end_time,
            'event_name': booking.event_name,
            'is_confirmed': has_payment or booking.status == 'approved'
        })
        
        # If any booking is confirmed with payment, mark the date
        if has_payment:
            booking_dates[date_str]['has_confirmed_booking'] = True
            
        # For simplicity, if there are 3 or more bookings, or if the booking spans the entire day
        # consider the date fully booked
        if len(booking_dates[date_str]['bookings']) >= 3:
            booking_dates[date_str]['time_slots_available'] = False
            booking_dates[date_str]['is_fully_booked'] = True
        
        # Check if any booking covers a significant portion of the day (e.g., 8+ hours)
        start_time = booking.start_time
        end_time = booking.end_time
        if start_time and end_time:
            duration = datetime.combine(today, end_time) - datetime.combine(today, start_time)
            if duration.seconds >= 8 * 3600 and has_payment:  # 8 hours or more and has payment
                booking_dates[date_str]['is_fully_booked'] = True
    
    # Create available time slots for dates without full-day bookings
    available_dates = []
    for d in range(30):
        current_date = today + timedelta(days=d)
        date_str = current_date.strftime('%Y-%m-%d')
        
        if date_str in booking_dates:
            # This date has some bookings
            day_info = booking_dates[date_str]
            
            # If there are confirmed bookings with payment AND the day is fully booked,
            # mark as fully booked
            if day_info['has_confirmed_booking'] and day_info['is_fully_booked']:
                status = 'fully_booked'
            # If there are confirmed bookings but time slots still available, mark as booked
            elif day_info['has_confirmed_booking']:
                status = 'booked'
            # If there are bookings but none confirmed and no slots available, mark as fully booked
            elif not day_info['time_slots_available']:
                status = 'fully_booked'
            # Otherwise, some time slots are available
            else:
                status = 'partially_booked'
                
            available_dates.append({
                'date': current_date,
                'has_bookings': True,
                'status': status,
                'bookings': day_info['bookings']
            })
        else:
            # This date has no bookings
            available_dates.append({
                'date': current_date,
                'has_bookings': False,
                'status': 'available',
                'bookings': []
            })
    
    # Get average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    
    context = {
        'venue': venue,
        'reviews': reviews,
        'available_dates': available_dates[:10],  # Only show first 10 for simplicity
        'all_available_dates': available_dates,
        'avg_rating': avg_rating,
    }
    return render(request, 'venues/venue_detail.html', context)

@login_required
@venue_manager_required
def manage_venues(request):
    """View for managing venues (for venue managers)"""
    venues = Venue.objects.filter(manager=request.user)
    return render(request, 'venues/manage_venues.html', {'venues': venues})

@login_required
@venue_manager_required
def add_venue(request):
    """View for adding a new venue"""
    if request.method == 'POST':
        form = VenueForm(request.POST)
        if form.is_valid():
            venue = form.save(commit=False)
            venue.manager = request.user
            venue.save()
            
            # Always ensure user is a venue manager
            if hasattr(request.user, 'profile'):
                request.user.profile.user_type = 'venue_manager'
                request.user.profile.save()
            
            messages.success(request, 'Venue added successfully!')
            return redirect('manage_venues')
    else:
        form = VenueForm()
    
    return render(request, 'venues/add_venue.html', {'form': form})

@login_required
@venue_manager_required
def edit_venue(request, venue_id):
    """View for editing a venue"""
    venue = get_object_or_404(Venue, id=venue_id, manager=request.user)
    
    if request.method == 'POST':
        form = VenueForm(request.POST, instance=venue)
        if form.is_valid():
            form.save()
            messages.success(request, 'Venue updated successfully!')
            return redirect('manage_venues')
    else:
        form = VenueForm(instance=venue)
    
    return render(request, 'venues/edit_venue.html', {'form': form, 'venue': venue})

@login_required
@venue_manager_required
def delete_venue(request, venue_id):
    """View for deleting a venue"""
    venue = get_object_or_404(Venue, id=venue_id, manager=request.user)
    
    if request.method == 'POST':
        venue.is_active = False
        venue.save()
        messages.success(request, 'Venue deleted successfully!')
        return redirect('manage_venues')
    
    return render(request, 'venues/delete_venue.html', {'venue': venue})

@login_required
@venue_manager_required
def manage_venue_images(request, venue_id):
    """View for managing venue images"""
    venue = get_object_or_404(Venue, id=venue_id, manager=request.user)
    images = VenueImage.objects.filter(venue=venue)
    
    if request.method == 'POST':
        form = VenueImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.venue = venue
            
            # If this is the first image, make it primary
            if not images.exists():
                image.is_primary = True
            
            image.save()
            messages.success(request, 'Image added successfully!')
            return redirect('manage_venue_images', venue_id=venue.id)
    else:
        form = VenueImageForm()
    
    context = {
        'venue': venue,
        'images': images,
        'form': form,
    }
    return render(request, 'venues/manage_venue_images.html', context)

@login_required
@venue_manager_required
def delete_venue_image(request, image_id):
    """View for deleting a venue image"""
    image = get_object_or_404(VenueImage, id=image_id, venue__manager=request.user)
    venue_id = image.venue.id
    
    if request.method == 'POST':
        # If deleting the primary image, set another image as primary if available
        if image.is_primary:
            other_image = VenueImage.objects.filter(venue_id=venue_id).exclude(id=image_id).first()
            if other_image:
                other_image.is_primary = True
                other_image.save()
        
        image.delete()
        messages.success(request, 'Image deleted successfully!')
        return redirect('manage_venue_images', venue_id=venue_id)
    
    return render(request, 'venues/delete_venue_image.html', {'image': image})

@login_required
@venue_manager_required
def set_primary_image(request, image_id):
    """View for setting an image as primary"""
    image = get_object_or_404(VenueImage, id=image_id, venue__manager=request.user)
    venue_id = image.venue.id
    
    # First, unset all primary images for this venue
    VenueImage.objects.filter(venue_id=venue_id).update(is_primary=False)
    
    # Set this image as primary
    image.is_primary = True
    image.save()
    
    messages.success(request, 'Primary image updated successfully!')
    return redirect('manage_venue_images', venue_id=venue_id)

@login_required
@venue_manager_required
def set_cover_image(request, image_id):
    """View for setting an image as cover"""
    image = get_object_or_404(VenueImage, id=image_id, venue__manager=request.user)
    venue_id = image.venue.id
    
    # First, unset all cover images for this venue
    VenueImage.objects.filter(venue_id=venue_id).update(is_cover=False)
    
    # Set this image as cover
    image.is_cover = True
    image.save()
    
    messages.success(request, 'Cover image updated successfully!')
    return redirect('manage_venue_images', venue_id=venue_id)

@login_required
@venue_manager_required
def venue_bookings(request, venue_id):
    """View for viewing bookings for a specific venue"""
    venue = get_object_or_404(Venue, id=venue_id, manager=request.user)
    bookings = Booking.objects.filter(venue=venue).order_by('-created_at')
    
    return render(request, 'venues/venue_bookings.html', {
        'venue': venue,
        'bookings': bookings,
    }) 