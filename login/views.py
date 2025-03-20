from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from .forms import CustomUserCreationForm,LoginForm


# Create your views here.


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # Redirect based on user type
            if user.user_type == 'venue_manager':
                return redirect('corehome56:manager_dashboard')
            else:
                return redirect('corehome56:regular_dashboard')
    else:
        form = CustomUserCreationForm()

    return render(request, 'login/register.html', {'form': form})


def logout_view(request):
    logout(request)  #clears the session
    return redirect('corehome56:home')  

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect based on user type
            if user.user_type == 'venue_manager':
                return redirect('corehome56:manager_dashboard')
            else:
                return redirect('corehome56:regular_dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    form=LoginForm()
    return render(request, 'login/login.html', {
        "form":form
    })


