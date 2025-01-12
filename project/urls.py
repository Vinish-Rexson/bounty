"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from django.views.generic import RedirectView
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.conf.urls.static import static
from channels.routing import ProtocolTypeRouter, URLRouter
from chat.routing import websocket_urlpatterns


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/dev/', views.dev_signup, name='dev_signup'),
    path('signup/customer/', views.customer_signup, name='customer_signup'),
    path('', include('social_django.urls', namespace='social')),
    path('dev/', include('dev.urls', namespace='dev')),
    path('choose-role/', views.choose_role, name='choose_role'),
    path('customer/', include('customer.urls', namespace='customer')),
    path('chat/', include('chat.urls', namespace='chat')),
    path('auth-redirect/', views.auth_redirect, name='auth_redirect'),
    path('general_login/', views.general_login, name='general_login'),
    path('home/', views.home, name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
