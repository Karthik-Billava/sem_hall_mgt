from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from .models import Booking, Payment
from .forms import BookingForm, PaymentForm
from venues.models import Venue, Availability
from notifications.signals import notify
from datetime import datetime, timedelta
import decimal

@login_required
def book_venue(request, venue_id):
    """View for booking a venue"""
    venue = get_object_or_404(Venue, id=venue_id, is_active=True)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.venue = venue
            
            # Calculate total cost
            start_time = booking.start_time
            end_time = booking.end_time
            duration_hours = (datetime.combine(datetime.today(), end_time) - 
                             datetime.combine(datetime.today(), start_time)).seconds / 3600
            booking.total_cost = venue.hourly_rate * decimal.Decimal(duration_hours)
            
            # Check if there's no conflicting booking
            conflicting_booking = Booking.objects.filter(
                venue=venue,
                date=booking.date,
                status__in=['pending', 'approved'],
            ).filter(
                Q(start_time__lt=booking.end_time, end_time__gt=booking.start_time)
            ).exists()
            
            # Check if venue has explicitly defined availability slots
            availability_exists = Availability.objects.filter(
                venue=venue,
                date=booking.date
            ).exists()
            
            if availability_exists:
                # If venue has explicitly defined availability slots, check that time slot is available
                is_available = Availability.objects.filter(
                    venue=venue,
                    date=booking.date,
                    start_time__lte=booking.start_time,
                    end_time__gte=booking.end_time,
                    is_available=True
                ).exists()
                
                if not is_available:
                    messages.error(request, 'The venue is not available for the selected time.')
                    return render(request, 'bookings/book_venue.html', {'form': form, 'venue': venue})
            
            # If there are no availability records for this date, we assume the venue is available
            # unless there's a conflicting booking
            
            if conflicting_booking:
                messages.error(request, 'There is already a booking for this time slot.')
                return render(request, 'bookings/book_venue.html', {'form': form, 'venue': venue})
            
            # Check if attendees exceed venue capacity
            if booking.attendees > venue.capacity:
                messages.error(request, f'The number of attendees exceeds the venue capacity of {venue.capacity}.')
                return render(request, 'bookings/book_venue.html', {'form': form, 'venue': venue})
            
            booking.save()
            
            # Notify venue manager
            notify.send(
                request.user,
                recipient=venue.manager,
                verb='requested a booking for',
                target=venue,
                action_object=booking,
                description=f"New booking request for {venue.name} on {booking.date}"
            )
            
            messages.success(request, 'Your booking request has been submitted and is pending approval.')
            return redirect('booking_detail', booking_id=booking.id)
    else:
        # Pre-fill date and time if provided in GET parameters
        initial_data = {}
        if 'date' in request.GET:
            initial_data['date'] = request.GET.get('date')
        if 'start_time' in request.GET:
            initial_data['start_time'] = request.GET.get('start_time')
        if 'end_time' in request.GET:
            initial_data['end_time'] = request.GET.get('end_time')
        
        form = BookingForm(initial=initial_data)
    
    return render(request, 'bookings/book_venue.html', {'form': form, 'venue': venue})

@login_required
def booking_detail(request, booking_id):
    """View for booking details"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check if user is authorized to view this booking
    if request.user != booking.user and request.user != booking.venue.manager:
        messages.error(request, 'You are not authorized to view this booking.')
        return redirect('home')
    
    # Check if payment exists
    try:
        payment = booking.payment
    except Payment.DoesNotExist:
        payment = None
    
    context = {
        'booking': booking,
        'payment': payment,
    }
    return render(request, 'bookings/booking_detail.html', context)

@login_required
def cancel_booking(request, booking_id):
    """View for cancelling a booking"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if booking.status == 'completed' or booking.status == 'cancelled':
        messages.error(request, 'This booking cannot be cancelled.')
        return redirect('booking_detail', booking_id=booking.id)
    
    if request.method == 'POST':
        booking.status = 'cancelled'
        booking.save()
        
        # Notify venue manager
        notify.send(
            request.user,
            recipient=booking.venue.manager,
            verb='cancelled a booking for',
            target=booking.venue,
            action_object=booking,
            description=f"Booking for {booking.venue.name} on {booking.date} has been cancelled"
        )
        
        messages.success(request, 'Your booking has been cancelled successfully.')
        return redirect('home')
    
    return render(request, 'bookings/cancel_booking.html', {'booking': booking})

@login_required
def approve_booking(request, booking_id):
    """View for approving a booking (for venue managers)"""
    booking = get_object_or_404(Booking, id=booking_id, venue__manager=request.user)
    
    if booking.status != 'pending':
        messages.error(request, 'This booking cannot be approved.')
        return redirect('booking_detail', booking_id=booking.id)
    
    if request.method == 'POST':
        booking.status = 'approved'
        booking.save()
        
        # Notify user
        notify.send(
            request.user,
            recipient=booking.user,
            verb='approved your booking for',
            target=booking.venue,
            action_object=booking,
            description=f"Your booking for {booking.venue.name} on {booking.date} has been approved"
        )
        
        messages.success(request, 'The booking has been approved successfully.')
        return redirect('venue_bookings', venue_id=booking.venue.id)
    
    return render(request, 'bookings/approve_booking.html', {'booking': booking})

@login_required
def reject_booking(request, booking_id):
    """View for rejecting a booking (for venue managers)"""
    booking = get_object_or_404(Booking, id=booking_id, venue__manager=request.user)
    
    if booking.status != 'pending':
        messages.error(request, 'This booking cannot be rejected.')
        return redirect('booking_detail', booking_id=booking.id)
    
    if request.method == 'POST':
        booking.status = 'rejected'
        booking.save()
        
        # Notify user
        notify.send(
            request.user,
            recipient=booking.user,
            verb='rejected your booking for',
            target=booking.venue,
            action_object=booking,
            description=f"Your booking for {booking.venue.name} on {booking.date} has been rejected"
        )
        
        messages.success(request, 'The booking has been rejected successfully.')
        return redirect('venue_bookings', venue_id=booking.venue.id)
    
    return render(request, 'bookings/reject_booking.html', {'booking': booking})

@login_required
def make_payment(request, booking_id):
    """View for making a payment for a booking"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if booking.status != 'approved':
        messages.error(request, 'Payment can only be made for approved bookings.')
        return redirect('booking_detail', booking_id=booking.id)
    
    # Check if payment already exists
    try:
        payment = booking.payment
        if payment.status == 'completed':
            messages.info(request, 'Payment has already been completed for this booking.')
            return redirect('booking_detail', booking_id=booking.id)
    except Payment.DoesNotExist:
        payment = None
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.booking = booking
            payment.amount = booking.total_cost
            payment.status = 'completed'  # In a real app, this would be handled by a payment gateway
            payment.save()
            
            # Notify venue manager
            notify.send(
                request.user,
                recipient=booking.venue.manager,
                verb='made a payment for',
                target=booking.venue,
                action_object=booking,
                description=f"Payment received for booking at {booking.venue.name} on {booking.date}"
            )
            
            messages.success(request, 'Your payment has been processed successfully.')
            return redirect('booking_detail', booking_id=booking.id)
    else:
        form = PaymentForm()
    
    return render(request, 'bookings/make_payment.html', {
        'form': form,
        'booking': booking,
    })

@login_required
def check_availability(request, venue_id):
    """AJAX view for checking venue availability"""
    venue = get_object_or_404(Venue, id=venue_id, is_active=True)
    date_str = request.GET.get('date')
    
    if not date_str:
        return JsonResponse({'error': 'Date is required'}, status=400)
    
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)
    
    # Get availabilities for the date
    availabilities = Availability.objects.filter(
        venue=venue,
        date=date,
        is_available=True
    ).order_by('start_time')
    
    # Get bookings for the date
    bookings = Booking.objects.filter(
        venue=venue,
        date=date,
        status__in=['pending', 'approved']
    )
    
    # Format the data for the response
    availability_data = []
    
    # If there are specific availability records, use them
    if availabilities.exists():
        for avail in availabilities:
            # Check if there's a conflicting booking
            is_booked = False
            for booking in bookings:
                if (booking.start_time < avail.end_time and booking.end_time > avail.start_time):
                    is_booked = True
                    break
            
            if not is_booked:
                availability_data.append({
                    'start_time': avail.start_time.strftime('%H:%M'),
                    'end_time': avail.end_time.strftime('%H:%M'),
                })
    else:
        # If no availability records, create default time slots (9 AM to 9 PM in 1-hour increments)
        # and exclude times that have bookings
        default_start = datetime.strptime('09:00', '%H:%M').time()
        default_end = datetime.strptime('21:00', '%H:%M').time()
        
        current_time = default_start
        while current_time < default_end:
            next_time = (datetime.combine(date, current_time) + timedelta(hours=1)).time()
            
            # Check if this time slot conflicts with any booking
            is_booked = False
            for booking in bookings:
                if (current_time < booking.end_time and next_time > booking.start_time):
                    is_booked = True
                    break
            
            if not is_booked:
                availability_data.append({
                    'start_time': current_time.strftime('%H:%M'),
                    'end_time': next_time.strftime('%H:%M'),
                })
                
            current_time = next_time
    
    return JsonResponse({'availabilities': availability_data}) 