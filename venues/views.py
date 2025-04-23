from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Venue, VenueImage, Availability
from .forms import VenueForm, VenueImageForm, AvailabilityForm
from accounts.models import Review
from bookings.models import Booking
from datetime import datetime, timedelta

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
    
    # Check availability for the next 30 days
    today = datetime.now().date()
    thirty_days_later = today + timedelta(days=30)
    availabilities = Availability.objects.filter(
        venue=venue,
        date__gte=today,
        date__lte=thirty_days_later,
        is_available=True
    ).order_by('date', 'start_time')
    
    # Get bookings for the next 30 days
    bookings = Booking.objects.filter(
        venue=venue,
        date__gte=today,
        date__lte=thirty_days_later,
        status__in=['pending', 'approved']
    )
    
    # If no explicit availability records, generate default ones
    availability_list = []
    if not availabilities.exists():
        # Create default availability for the next 7 days (9 AM to 9 PM)
        for day_offset in range(7):
            current_date = today + timedelta(days=day_offset)
            default_start = datetime.strptime('09:00', '%H:%M').time()
            default_end = datetime.strptime('21:00', '%H:%M').time()
            
            # Check for conflicts with bookings
            day_bookings = [b for b in bookings if b.date == current_date]
            if not day_bookings:
                # No bookings for this day, so the whole day is available
                availability_list.append({
                    'date': current_date,
                    'start_time': default_start,
                    'end_time': default_end
                })
            else:
                # There are bookings, find available times
                current_time = default_start
                while current_time < default_end:
                    next_time = (datetime.combine(current_date, current_time) + timedelta(hours=1)).time()
                    
                    is_booked = False
                    for booking in day_bookings:
                        if (current_time < booking.end_time and next_time > booking.start_time):
                            is_booked = True
                            break
                    
                    if not is_booked:
                        availability_list.append({
                            'date': current_date,
                            'start_time': current_time,
                            'end_time': next_time
                        })
                    
                    current_time = next_time
    else:
        # Convert queryset to list for template use
        for avail in availabilities:
            # Check if there's a conflicting booking
            is_booked = False
            day_bookings = [b for b in bookings if b.date == avail.date]
            for booking in day_bookings:
                if (booking.start_time < avail.end_time and booking.end_time > avail.start_time):
                    is_booked = True
                    break
            
            if not is_booked:
                availability_list.append({
                    'date': avail.date,
                    'start_time': avail.start_time,
                    'end_time': avail.end_time
                })
    
    # Get average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    
    context = {
        'venue': venue,
        'reviews': reviews,
        'availabilities': availability_list,
        'avg_rating': avg_rating,
    }
    return render(request, 'venues/venue_detail.html', context)

@login_required
def manage_venues(request):
    """View for managing venues (for venue managers)"""
    venues = Venue.objects.filter(manager=request.user)
    return render(request, 'venues/manage_venues.html', {'venues': venues})

@login_required
def add_venue(request):
    """View for adding a new venue"""
    if request.method == 'POST':
        form = VenueForm(request.POST)
        if form.is_valid():
            venue = form.save(commit=False)
            venue.manager = request.user
            venue.save()
            messages.success(request, 'Venue added successfully!')
            return redirect('manage_venues')
    else:
        form = VenueForm()
    
    return render(request, 'venues/add_venue.html', {'form': form})

@login_required
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
def set_primary_image(request, image_id):
    """View for setting a venue image as primary"""
    image = get_object_or_404(VenueImage, id=image_id, venue__manager=request.user)
    venue_id = image.venue.id
    
    # Clear primary flag on all images for this venue
    VenueImage.objects.filter(venue_id=venue_id).update(is_primary=False)
    
    # Set this image as primary
    image.is_primary = True
    image.save()
    
    messages.success(request, 'Primary image updated successfully!')
    return redirect('manage_venue_images', venue_id=venue_id)

@login_required
def set_cover_image(request, image_id):
    """View for setting a venue image as cover image"""
    image = get_object_or_404(VenueImage, id=image_id, venue__manager=request.user)
    venue_id = image.venue.id
    
    # Clear cover flag on all images for this venue
    VenueImage.objects.filter(venue_id=venue_id).update(is_cover=False)
    
    # Set this image as cover
    image.is_cover = True
    image.save()
    
    messages.success(request, 'Cover image updated successfully!')
    return redirect('manage_venue_images', venue_id=venue_id)

@login_required
def manage_availability(request, venue_id):
    """View for managing venue availability"""
    venue = get_object_or_404(Venue, id=venue_id, manager=request.user)
    availabilities = Availability.objects.filter(venue=venue).order_by('date', 'start_time')
    
    if request.method == 'POST':
        form = AvailabilityForm(request.POST)
        if form.is_valid():
            availability = form.save(commit=False)
            availability.venue = venue
            availability.save()
            messages.success(request, 'Availability added successfully!')
            return redirect('manage_availability', venue_id=venue.id)
    else:
        form = AvailabilityForm()
    
    context = {
        'venue': venue,
        'availabilities': availabilities,
        'form': form,
    }
    return render(request, 'venues/manage_availability.html', context)

@login_required
def delete_availability(request, availability_id):
    """View for deleting venue availability"""
    availability = get_object_or_404(Availability, id=availability_id, venue__manager=request.user)
    venue_id = availability.venue.id
    
    if request.method == 'POST':
        availability.delete()
        messages.success(request, 'Availability deleted successfully!')
        return redirect('manage_availability', venue_id=venue_id)
    
    return render(request, 'venues/delete_availability.html', {'availability': availability})

@login_required
def venue_bookings(request, venue_id):
    """View for viewing bookings for a specific venue"""
    venue = get_object_or_404(Venue, id=venue_id, manager=request.user)
    bookings = Booking.objects.filter(venue=venue).order_by('-created_at')
    
    return render(request, 'venues/venue_bookings.html', {
        'venue': venue,
        'bookings': bookings,
    }) 