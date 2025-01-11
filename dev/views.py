from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import ProfileForm, ProjectForm
from .models import Profile, Project
from django.contrib import messages
from django.conf import settings
from django.views.generic import CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

def is_developer(user):
    return user.groups.filter(name=settings.DEVELOPER_GROUP).exists()

developer_required = user_passes_test(is_developer, login_url='login')

@developer_required
@login_required
def dashboard(request):
    profile = request.user.profile
    comments = profile.comments.all().order_by('-created_at')
    return render(request, 'dev/dashboard.html', {
        'profile': profile,
        'comments': comments
    })

@developer_required
@login_required
def profile(request):
    try:
        profile = request.user.profile
        # Get projects ordered by creation date
        projects = profile.projects.all().order_by('-created_at')
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)
        projects = []
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            
            # Update required fields to match our new field names
            required_fields = [
                'display_name', 'title', 'years_of_experience', 
                'hourly_rate', 'github_url', 'timezone'
            ]
            
            # Check availability fields based on type
            availability_type = form.cleaned_data['availability_type']
            if availability_type == 'weekday':
                required_fields.extend(['weekday_from', 'weekday_to'])
            elif availability_type == 'weekend':
                required_fields.extend(['weekend_from', 'weekend_to'])
            else:  # temporary
                required_fields.extend(['temp_from', 'temp_to'])
            
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
    
    return render(request, 'dev/profile.html', {
        'form': form,
        'profile': profile,
        'projects': projects
    })

def home(request):
    return render(request, 'dev/index.html')

class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'dev/project_form.html'
    success_url = reverse_lazy('dev:profile')

class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'dev/project_detail.html'
    context_object_name = 'project'

class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'dev/project_form.html'

@require_http_methods(["POST"])
@login_required
def project_create_api(request):
    data = json.loads(request.body)
    project = Project.objects.create(
        name=data['name'],
        readme=data['readme'],
        deployed_url=data['deployed_url'],
        github_url=data['github_url'],
        client=data['client'],
        profile=request.user.profile
    )
    
    return JsonResponse({
        'id': project.id,
        'name': project.name,
        'client': project.client
    })