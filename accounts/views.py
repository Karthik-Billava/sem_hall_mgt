from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages


from .models import UserProfile
from .forms import UserProfileForm

# Create your views here.
@login_required
def profile_view(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={'user_type': user.user_type}
    )
    return render(request, "accounts/profile.html", {
        'user': user,
        'profile': profile,
    })

def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        profile, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={'user_type': request.user.user_type}
        )
        form = UserProfileForm(instance=profile)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})

