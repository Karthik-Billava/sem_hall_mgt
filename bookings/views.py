from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from .models import Booking, Payment
from .forms import BookingForm, PaymentForm
from venues.models import Venue
from notifications.signals import notify
from notifications.models import Notification
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
            
            if conflicting_booking:
                messages.error(request, 'There is already a booking for this time slot.')
                return render(request, 'bookings/book_venue.html', {'form': form, 'venue': venue})
            
            # Check if attendees exceed venue capacity
            if booking.attendees > venue.capacity:
                messages.error(request, f'The number of attendees exceeds the venue capacity of {venue.capacity}.')
                return render(request, 'bookings/book_venue.html', {'form': form, 'venue': venue})
            
            booking.save()
            
            # Check if a similar notification already exists (prevent duplicates)
            existing_notifications = Notification.objects.filter(
                recipient=venue.manager,
                actor_object_id=request.user.id,
                target_object_id=venue.id,
                action_object_content_type__model='booking',
                action_object_object_id=booking.id,
                verb='requested a booking for'
            )
            
            # Only send notification if no similar notification exists
            if not existing_notifications.exists():
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
        
        # Check if a similar notification already exists (prevent duplicates)
        existing_notifications = Notification.objects.filter(
            recipient=booking.venue.manager,
            actor_object_id=request.user.id,
            target_object_id=booking.venue.id,
            action_object_content_type__model='booking',
            action_object_object_id=booking.id,
            verb='cancelled a booking for'
        )
        
        # Only send notification if no similar notification exists
        if not existing_notifications.exists():
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
        booking.approval_time = timezone.now()  # Set the approval time
        booking.save()
        
        # Check if a similar notification already exists (prevent duplicates)
        existing_notifications = Notification.objects.filter(
            recipient=booking.user,
            actor_object_id=request.user.id,
            target_object_id=booking.venue.id,
            action_object_content_type__model='booking',
            action_object_object_id=booking.id,
            verb='approved your booking for'
        )
        
        # Only send notification if no similar notification exists
        if not existing_notifications.exists():
            # Notify user
            notify.send(
                request.user,
                recipient=booking.user,
                verb='approved your booking for',
                target=booking.venue,
                action_object=booking,
                description=f"Your booking for {booking.venue.name} on {booking.date} has been approved. Please complete payment within 24 hours."
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
        
        # Check if a similar notification already exists (prevent duplicates)
        existing_notifications = Notification.objects.filter(
            recipient=booking.user,
            actor_object_id=request.user.id,
            target_object_id=booking.venue.id,
            action_object_content_type__model='booking',
            action_object_object_id=booking.id,
            verb='rejected your booking for'
        )
        
        # Only send notification if no similar notification exists
        if not existing_notifications.exists():
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
            
            # Check if a similar notification already exists (prevent duplicates)
            existing_notifications = Notification.objects.filter(
                recipient=booking.venue.manager,
                actor_object_id=request.user.id,
                target_object_id=booking.venue.id,
                action_object_content_type__model='booking',
                action_object_object_id=booking.id,
                verb='made a payment for'
            )
            
            # Only send notification if no similar notification exists
            if not existing_notifications.exists():
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
    
    return render(request, 'bookings/make_payment.html', {'form': form, 'booking': booking})

@login_required
def check_availability(request, venue_id):
    """AJAX view to check venue availability for a specific date"""
    venue = get_object_or_404(Venue, id=venue_id)
    
    date_str = request.GET.get('date')
    
    if not date_str:
        return JsonResponse({'available': False, 'message': 'No date provided'})
    
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'available': False, 'message': 'Invalid date format'})
    
    # Get bookings for this date
    bookings = Booking.objects.filter(
        venue=venue,
        date=date,
        status__in=['pending', 'approved']
    ).values('start_time', 'end_time')
    
    # If there are no bookings, the entire day is available
    if not bookings:
        return JsonResponse({
            'available': True,
            'time_slots': [{'start': '09:00', 'end': '17:00'}],
            'bookings': []
        })
    
    # Convert bookings to a list of dictionaries with string times
    booking_list = []
    for booking in bookings:
        booking_list.append({
            'start': booking['start_time'].strftime('%H:%M'),
            'end': booking['end_time'].strftime('%H:%M')
        })
    
    # Create a list of available time slots (this is simplified)
    # In a real application, you would need a more sophisticated algorithm
    # to find non-overlapping time slots
    
    # For now, just return a message that there are some bookings
    return JsonResponse({
        'available': True,
        'message': 'There are some existing bookings on this date',
        'bookings': booking_list
    })

@login_required
def my_bookings(request):
    """View for listing user's bookings"""
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'bookings/my_bookings.html', {'bookings': bookings})
    
@login_required
def complete_booking(request, booking_id):
    """View for completing a booking (for venue managers)"""
    booking = get_object_or_404(Booking, id=booking_id, venue__manager=request.user)
    
    if booking.status != 'approved':
        messages.error(request, 'Only approved bookings can be marked as completed.')
        return redirect('booking_detail', booking_id=booking.id)
    
    if request.method == 'POST':
        booking.status = 'completed'
        booking.save()
        
        # Check if a similar notification already exists (prevent duplicates)
        existing_notifications = Notification.objects.filter(
            recipient=booking.user,
            actor_object_id=request.user.id,
            target_object_id=booking.venue.id,
            action_object_content_type__model='booking',
            action_object_object_id=booking.id,
            verb='marked your booking as completed for'
        )
        
        # Only send notification if no similar notification exists
        if not existing_notifications.exists():
            # Notify user that booking is completed
            notify.send(
                request.user,
                recipient=booking.user,
                verb='marked your booking as completed for',
                target=booking.venue,
                action_object=booking,
                description=f"Your booking for {booking.venue.name} on {booking.date} has been completed."
            )
        
        # Check if a review request notification already exists
        review_request_notifications = Notification.objects.filter(
            recipient=booking.user,
            actor_object_id=request.user.id,
            target_object_id=booking.venue.id,
            action_object_content_type__model='booking',
            action_object_object_id=booking.id,
            verb='requests a review for'
        )
        
        # Send a notification asking for a review if none exists
        if not review_request_notifications.exists():
            notify.send(
                request.user,
                recipient=booking.user,
                verb='requests a review for',
                target=booking.venue,
                action_object=booking,
                description=f"Please share your experience at {booking.venue.name}. Your feedback helps others make better choices!"
            )
        
        messages.success(request, 'The booking has been marked as completed.')
        return redirect('venue_bookings', venue_id=booking.venue.id)
    
    return render(request, 'bookings/complete_booking.html', {'booking': booking}) 