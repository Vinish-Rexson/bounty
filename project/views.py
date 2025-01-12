from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import Group
from django.conf import settings
from django.urls import reverse

def login_view(request):
    print(request.user.is_authenticated)
    if request.user.is_authenticated:
        # Check if user belongs to both groups
        is_developer = request.user.groups.filter(name=settings.DEVELOPER_GROUP).exists()
        is_customer = request.user.groups.filter(name=settings.CUSTOMER_GROUP).exists()
        
        print(is_developer, is_customer)
        # Always show choose_role for users in both groups
        if is_developer and is_customer:
            return redirect('choose_role')
        elif is_developer:
            return redirect('dev:dashboard')
        elif is_customer:
            return redirect('customer:dashboard')
        else:
            return redirect('general_login')

    if request.method == 'POST':
        print(request.POST)
        print("after post")
        form = AuthenticationForm(data=request.POST)
        print(form.is_valid())
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Check groups after login
            is_developer = user.groups.filter(name=settings.DEVELOPER_GROUP).exists()
            is_customer = user.groups.filter(name=settings.CUSTOMER_GROUP).exists()
            
            # Always redirect to choose_role if user is in both groups
            if is_developer and is_customer:
                return redirect('choose_role')
            elif is_developer:
                return redirect('dev:dashboard')
            elif is_customer:
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
            
            # Check if user is already a customer
            is_customer = user.groups.filter(name=settings.CUSTOMER_GROUP).exists()
            
            user = authenticate(username=user.username,
                              password=form.cleaned_data['password1'],
                              backend='django.contrib.auth.backends.ModelBackend')
            login(request, user)
            
            # Redirect to choose_role if user is in both groups
            if is_customer:
                return redirect('choose_role')
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
            
            # Check if user is already a developer
            is_developer = user.groups.filter(name=settings.DEVELOPER_GROUP).exists()
            
            user = authenticate(username=user.username,
                              password=form.cleaned_data['password1'],
                              backend='django.contrib.auth.backends.ModelBackend')
            login(request, user)
            
            # Redirect to choose_role if user is in both groups
            if is_developer:
                return redirect('choose_role')
            return redirect('customer:dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'customer/signup.html', {'form': form})
@login_required
def general_login(request):
    user= request.user
    print(user.is_authenticated)
    if request.method == "POST":
        print(request.POST)  # Debugging output
        form = UserCreationForm(request.POST)
        print(str(form) + "this is usercreationform")

        if request.POST.get('dev')=='developer':
            print(form.is_valid())
            print(form.errors)
            print(request.POST.get('dev'))
            
            dev_group = Group.objects.get_or_create(name=settings.DEVELOPER_GROUP)[0]
            user.groups.add(dev_group)
            
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('dev:dashboard')

        elif request.POST.get('customer')=='customer':
    
            customer_group = Group.objects.get_or_create(name=settings.CUSTOMER_GROUP)[0]
            user.groups.add(customer_group)
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('customer:dashboard')

        # Invalid form handling
        return redirect('general_login')
    return render(request, 'choose_login.html')

@login_required
def choose_role(request):
    if not request.user.is_authenticated:
        return redirect('login')
    is_developer = request.user.groups.filter(name=settings.DEVELOPER_GROUP).exists()
    is_customer = request.user.groups.filter(name=settings.CUSTOMER_GROUP).exists()
    
    # Only show this page if user belongs to both groups
    print(is_developer, is_customer)
    if not (is_developer and is_customer):
        if is_developer:
            return redirect('dev:dashboard')
        elif is_customer:
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
    is_developer = request.user.groups.filter(name=settings.DEVELOPER_GROUP).exists()
    is_customer = request.user.groups.filter(name=settings.CUSTOMER_GROUP).exists()
    
    # Always show choose_role for users in both groups
    if is_developer and is_customer:
        return redirect('choose_role')
    elif is_developer:
        return redirect('dev:dashboard')
    elif is_customer:
        return redirect('customer:dashboard')
    else:
        return redirect('general_login')
    # return redirect('home') 

def home(request):
    return render(request, 'index.html')
