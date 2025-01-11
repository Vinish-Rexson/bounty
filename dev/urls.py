from django.urls import path
from . import views
from django.views.generic import CreateView, DetailView, UpdateView

app_name = 'dev'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('home/', views.home, name='home'),
    path('projects/', views.browse_projects, name='browse_projects'),
    path('projects/<int:project_id>/request/', views.request_project, name='request_project'),
    path('requests/', views.view_requests, name='view_requests'),
    path('requests/<int:request_id>/handle/', views.handle_request, name='handle_request'),
] 