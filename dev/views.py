from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm
from .models import Profile
from django.contrib import messages

@login_required
def dashboard(request):
    return render(request, 'dev/dashboard.html')

@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            
            # Check if all required fields are filled (excluding certifications and education)
            required_fields = [
                'display_name', 'title', 'years_of_experience', 
                'hourly_rate', 'github_url', 'timezone',
                'available_from', 'available_to'
            ]
            
            is_complete = all(getattr(profile, field) for field in required_fields)
            
            if is_complete and form.cleaned_data['skills']:
                profile.is_profile_completed = True
                profile.is_verified = True  # Auto-verify when profile is complete
            
            profile.save()
            form.save_m2m()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('dev:dashboard')
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, 'dev/profile.html', {'form': form})
