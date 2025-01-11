from django.conf import settings
from django.contrib.auth.models import Group
from django.shortcuts import redirect

def assign_user_group(backend, user, response, *args, **kwargs):
    """Assign user to appropriate group based on the signup path"""
    
    # Get the next parameter from the session
    request = kwargs.get('request')
    if not request:
        return
        
    next_path = request.session.get('next', '')
    
    # Assign group based on next parameter
    if 'signup/dev' in next_path:
        group = Group.objects.get_or_create(name=settings.DEVELOPER_GROUP)[0]
        user.groups.add(group)
        # Only set redirect if user isn't already a customer
        if not user.groups.filter(name=settings.CUSTOMER_GROUP).exists():
            request.session['redirect_url'] = 'dev:dashboard'
        else:
            request.session['redirect_url'] = 'choose_role'
            
    elif 'signup/customer' in next_path:
        group = Group.objects.get_or_create(name=settings.CUSTOMER_GROUP)[0]
        user.groups.add(group)
        # Only set redirect if user isn't already a developer
        if not user.groups.filter(name=settings.DEVELOPER_GROUP).exists():
            request.session['redirect_url'] = 'customer:dashboard'
        else:
            request.session['redirect_url'] = 'choose_role' 