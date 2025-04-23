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
    
    if request.is_ajax():
        return JsonResponse({'status': 'success'})
    
    return redirect('notification_list')

@login_required
def mark_all_as_read(request):
    """View for marking all notifications as read"""
    request.user.notifications.mark_all_as_read()
    
    if request.is_ajax():
        return JsonResponse({'status': 'success'})
    
    return redirect('notification_list')

@login_required
def delete_notification(request, notification_id):
    """View for deleting a notification"""
    notification = get_object_or_404(
        Notification, 
        recipient=request.user,
        id=notification_id
    )
    notification.delete()
    
    if request.is_ajax():
        return JsonResponse({'status': 'success'})
    
    messages.success(request, 'Notification deleted successfully.')
    return redirect('notification_list')

@login_required
def notification_settings(request):
    """View for managing notification settings"""
    try:
        settings = request.user.notification_settings
    except NotificationSetting.DoesNotExist:
        settings = NotificationSetting.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = NotificationSettingForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notification settings updated successfully.')
            return redirect('notification_settings')
    else:
        form = NotificationSettingForm(instance=settings)
    
    return render(request, 'notifications/notification_settings.html', {'form': form}) 