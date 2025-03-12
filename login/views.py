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
            redirect_path = reverse("corehome56:home")
            return HttpResponseRedirect(redirect_path)
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
            return redirect('corehome56:home')
        else:
            messages.error(request, 'Invalid username or password')
    form=LoginForm()
    return render(request, 'login/login.html', {
        "form":form
    })


