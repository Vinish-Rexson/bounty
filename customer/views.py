from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from dev.models import Profile as DevProfile
from .models import CustomerProfile, Project
from .forms import CustomerProfileForm, ProjectForm
from django.conf import settings

def is_customer(user):
    return user.groups.filter(name=settings.CUSTOMER_GROUP).exists()

customer_required = user_passes_test(is_customer, login_url='login')

@customer_required
@login_required
def dashboard(request):
    customer_profile, created = CustomerProfile.objects.get_or_create(user=request.user)
    projects = Project.objects.filter(customer=customer_profile)
    return render(request, 'customer/dashboard.html', {
        'projects': projects
    })

@customer_required
@login_required
def browse_developers(request):
    developers = DevProfile.objects.filter(is_verified=True, is_available=True)
    return render(request, 'customer/browse_developers.html', {
        'developers': developers
    })

@login_required
def developer_profile(request, dev_id):
    developer = DevProfile.objects.get(id=dev_id)
    return render(request, 'customer/developer_profile.html', {
        'developer': developer
    })

@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            customer_profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
            project.customer = customer_profile
            project.save()
            form.save_m2m()
            return redirect('customer:dashboard')
    else:
        form = ProjectForm()
    return render(request, 'customer/create_project.html', {'form': form})
