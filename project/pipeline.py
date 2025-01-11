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
    current_path = request.path  # Get the current path
    
    # Check existing group memberships
    is_developer = user.groups.filter(name=settings.DEVELOPER_GROUP).exists()
    is_customer = user.groups.filter(name=settings.CUSTOMER_GROUP).exists()
    
    # Assign group based on current path or next parameter
    if 'signup/dev' in next_path or 'signup/dev' in current_path:
        group = Group.objects.get_or_create(name=settings.DEVELOPER_GROUP)[0]
        user.groups.add(group)
        if is_customer:  # User is now in both groups
            request.session['next'] = '/choose-role/'
        else:
            request.session['redirect_url'] = 'dev:dashboard'
            
    elif 'signup/customer' in next_path or 'signup/customer' in current_path:
        group = Group.objects.get_or_create(name=settings.CUSTOMER_GROUP)[0]
        user.groups.add(group)
        if is_developer:  # User is now in both groups
            request.session['next'] = '/choose-role/'
        else:
            request.session['redirect_url'] = 'customer:dashboard' 