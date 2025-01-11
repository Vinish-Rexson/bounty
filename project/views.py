from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import Group
from django.conf import settings
from django.urls import reverse

def login_view(request):
    if request.user.is_authenticated:
        # Check user groups and redirect accordingly
        if request.user.groups.filter(name=settings.DEVELOPER_GROUP).exists():
            return redirect('dev:dashboard')
        elif request.user.groups.filter(name=settings.CUSTOMER_GROUP).exists():
            return redirect('customer:dashboard')
        else:
            # If no group is assigned, redirect to choose_role
            return redirect('choose_role')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if user.groups.filter(name=settings.DEVELOPER_GROUP).exists():
                    return redirect('dev:dashboard')
                elif user.groups.filter(name=settings.CUSTOMER_GROUP).exists():
                    return redirect('customer:dashboard')
                    
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def dev_signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            dev_group = Group.objects.get_or_create(name=settings.DEVELOPER_GROUP)[0]
            user.groups.add(dev_group)
            user = authenticate(username=user.username,
                              password=form.cleaned_data['password1'],
                              backend='django.contrib.auth.backends.ModelBackend')
            login(request, user)
            return redirect('dev:dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'dev/signup.html', {'form': form})

def customer_signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            customer_group = Group.objects.get_or_create(name=settings.CUSTOMER_GROUP)[0]
            user.groups.add(customer_group)
            user = authenticate(username=user.username,
                              password=form.cleaned_data['password1'],
                              backend='django.contrib.auth.backends.ModelBackend')
            login(request, user)
            return redirect('customer:dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'customer/signup.html', {'form': form})

@login_required
def choose_role(request):
    # Only show this page if user belongs to both groups
    if not (request.user.groups.filter(name=settings.DEVELOPER_GROUP).exists() and 
            request.user.groups.filter(name=settings.CUSTOMER_GROUP).exists()):
        if request.user.groups.filter(name=settings.DEVELOPER_GROUP).exists():
            return redirect('dev:dashboard')
        elif request.user.groups.filter(name=settings.CUSTOMER_GROUP).exists():
            return redirect('customer:dashboard')
    
    if request.method == 'POST':
        role = request.POST.get('role')
        if role == 'developer':
            return redirect('dev:dashboard')
        elif role == 'customer':
            return redirect('customer:dashboard')
    return render(request, 'choose_role.html')

def logout_view(request):
    logout(request)
    return redirect('login') 




@login_required
def auth_redirect(request):
    """Handle redirects after authentication"""
    # Get redirect URL from session
    redirect_url = request.session.get('redirect_url')
    if redirect_url:
        # Clear the session variable
        del request.session['redirect_url']
        return redirect(redirect_url)
    
    # Default redirect based on user groups
    if request.user.groups.filter(name=settings.DEVELOPER_GROUP).exists():
        return redirect('dev:dashboard')
    elif request.user.groups.filter(name=settings.CUSTOMER_GROUP).exists():
        return redirect('customer:dashboard')
    return redirect('choose_role') 