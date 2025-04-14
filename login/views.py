from django.shortcuts import render, redirect
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse

from .forms import CustomUserCreationForm,LoginForm
from .models import CustomUser as cu
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


def regular_dashboard(request,slug):
    user=cu.objects.get(username=slug)
    return render(request, "login/regular_dashboard.html",{
        "user":user
    })


def manager_dashboard(request,*args, **kwargs):
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
            username=request.POST['username'] # Adds the usename to url (traditional way)
            redirect_url=reverse('manager_dashboard',args=[username])
            if user.user_type == 'venue_manager':
                return HttpResponseRedirect(redirect_url)
            else:
                return HttpResponseRedirect(redirect_url)
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
        redirect_url=reverse('manager_dashboard',args=[username])
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect based on user type
            if user.user_type == 'venue_manager':
                return redirect('manager_dashboard',username) # Adds the usename to url
            else:
                return redirect('regular_dashboard',username)
        else:
            messages.error(request, 'Invalid username or password')
    form=LoginForm()
    return render(request, 'login/login.html', {
        "form":form
    })


