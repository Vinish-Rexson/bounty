from django.urls import path
from . import views
from django.views.generic import CreateView, DetailView, UpdateView

app_name = 'dev'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('home/', views.home, name='home'),
    path('project/new/', views.ProjectCreateView.as_view(), name='project_create'),
    path('project/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('project/<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='project_update'),
    path('project/create/', views.project_create_api, name='project_create_api'),
    path('projects/', views.browse_projects, name='browse_projects'),
    path('projects/<int:project_id>/request/', views.request_project, name='request_project'),
    path('requests/<int:request_id>/handle/', 
         views.handle_customer_request, 
         name='handle_customer_request'),
] 