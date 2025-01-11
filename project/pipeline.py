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
        # Set redirect URL in session
        request.session['redirect_url'] = 'dev:dashboard'
    elif 'signup/customer' in next_path:
        group = Group.objects.get_or_create(name=settings.CUSTOMER_GROUP)[0]
        user.groups.add(group)
        # Set redirect URL in session
        request.session['redirect_url'] = 'customer:dashboard' 