from django.shortcuts import render, redirect
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import CustomUserCreationForm,LoginForm
# Create your views here.
def home(request):
    # If user is authenticated, redirect to appropriate dashboard
    if request.user.is_authenticated:
        if request.user.user_type == 'venue_manager':
            return render(request, "login/manager_dashboard.html")
        else:  # regular user
            return render(request, "login/regular_dashboard.html")
    
    # If not authenticated, show general home page
    return render(request, "login/home.html")

@login_required
def regular_dashboard(request):
    return render(request, "login/regular_dashboard.html")

@login_required
def manager_dashboard(request):
    # Check if user is a venue manager
    if request.user.user_type != 'venue_manager':
        return render(request, "login/regular_dashboard.html")
    
    return render(request, "login/manager_dashboard.html") 

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # Redirect based on user type
            if user.user_type == 'venue_manager':
                return redirect('manager_dashboard')
            else:
                return redirect('regular_dashboard')
    else:
        form = CustomUserCreationForm()

    return render(request, 'login/register.html', {'form': form})


def logout_view(request):
    logout(request)  #clears the session
    return redirect('home')  

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect based on user type
            if user.user_type == 'venue_manager':
                return redirect('manager_dashboard')
            else:
                return redirect('regular_dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    form=LoginForm()
    return render(request, 'login/login.html', {
        "form":form
    })


