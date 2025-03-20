from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

def home(request):
    # If user is authenticated, redirect to appropriate dashboard
    if request.user.is_authenticated:
        if request.user.user_type == 'venue_manager':
            return render(request, "core/manager_dashboard.html")
        else:  # regular user
            return render(request, "core/regular_dashboard.html")
    
    # If not authenticated, show general home page
    return render(request, "core/home.html")

@login_required
def regular_dashboard(request):
    return render(request, "core/regular_dashboard.html")

@login_required
def manager_dashboard(request):
    # Check if user is a venue manager
    if request.user.user_type != 'venue_manager':
        return render(request, "core/regular_dashboard.html")
    
    return render(request, "core/manager_dashboard.html") 