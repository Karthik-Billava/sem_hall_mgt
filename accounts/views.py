from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile, Review
from .forms import UserProfileForm, ReviewForm
from bookings.models import Booking
from venues.models import Venue

@login_required
def profile_view(request):
    """View for user profile"""
    user = request.user
    profile = user.profile
    bookings = Booking.objects.filter(user=user).order_by('-created_at')
    
    context = {
        'user': user,
        'profile': profile,
        'bookings': bookings,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile(request):
    """View for editing user profile"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user.profile)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})

@login_required
def booking_history(request):
    """View for user booking history"""
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/booking_history.html', {'bookings': bookings})

@login_required
def add_review(request, venue_id):
    """View for adding a review"""
    venue = get_object_or_404(Venue, id=venue_id, is_active=True)
    
    # Prevent venue managers from reviewing their own venues
    if venue.manager == request.user:
        messages.error(request, 'You cannot review your own venue.')
        return redirect('venue_detail', venue_id=venue_id)
    
    # Check if user has already reviewed this venue
    existing_review = Review.objects.filter(user=request.user, venue=venue).first()
    if existing_review:
        messages.info(request, 'You have already reviewed this venue. You can edit your existing review.')
        return redirect('edit_review', review_id=existing_review.id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.venue = venue
            review.save()
            messages.success(request, 'Your review has been added successfully!')
            return redirect('venue_detail', venue_id=venue_id)
    else:
        form = ReviewForm()
    
    return render(request, 'accounts/add_review.html', {'form': form, 'venue': venue})

@login_required
def edit_review(request, review_id):
    """View for editing a review"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    venue = review.venue
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your review has been updated successfully!')
            return redirect('venue_detail', venue_id=venue.id)
    else:
        form = ReviewForm(instance=review)
    
    return render(request, 'accounts/edit_review.html', {
        'form': form, 
        'review': review,
        'venue': venue
    })

@login_required
def delete_review(request, review_id):
    """View for deleting a review"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    venue = review.venue
    
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Your review has been deleted successfully!')
        return redirect('venue_detail', venue_id=venue.id)
    
    return render(request, 'accounts/delete_review.html', {
        'review': review,
        'venue': venue
    }) 