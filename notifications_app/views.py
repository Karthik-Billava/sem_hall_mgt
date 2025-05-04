from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from notifications.models import Notification
from .models import NotificationSetting
from .forms import NotificationSettingForm

@login_required
def notification_list(request):
    """View for listing user notifications"""
    notifications = request.user.notifications.all()
    return render(request, 'notifications/notification_list.html', {'notifications': notifications})

@login_required
def mark_as_read(request, notification_id):
    """View for marking a notification as read"""
    notification = get_object_or_404(
        Notification, 
        recipient=request.user,
        id=notification_id
    )
    notification.mark_as_read()
    
    # Check if it's an AJAX request based on HTTP header
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    return redirect('notification_list')

@login_required
def mark_all_as_read(request):
    """View for marking all notifications as read"""
    request.user.notifications.mark_all_as_read()
    
    # Check if it's an AJAX request based on HTTP header
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    return redirect('notification_list')

@login_required
def delete_notification(request, notification_id):
    """View for deleting a notification"""
    try:
        # First try to find the notification by recipient and ID
        notification = Notification.objects.get(
            recipient=request.user,
            id=notification_id
        )
        notification.delete()
        
        # Check if it's an AJAX request based on HTTP header
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
        
        messages.success(request, 'Notification deleted successfully.')
    except Notification.DoesNotExist:
        # If notification doesn't exist, just inform the user and continue
        messages.warning(request, 'The notification has already been deleted or does not exist.')
    
    return redirect('notification_list')

