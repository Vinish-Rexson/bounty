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
    path('project/create/', views.project_create_api, name='project_create_api'),
    path('handle-customer-request/<int:request_id>/', views.handle_customer_request, name='handle_customer_request'),
    path('dev_project/new/', views.ProjectCreateView.as_view(), name='dev_project_create'),
    path('dev_project/<int:pk>/', views.ProjectDetailView.as_view(), name='dev_project_detail'),
    path('dev_project/<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='dev_project_update'),
    path('dev_project/<int:pk>/update/', views.project_update_api, name='project_update_api'),
    path('my-projects/', views.my_projects, name='my_projects'),
    path('projects/list/', views.projects, name='projects'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('customer-project/<int:project_id>/', views.customer_project_detail, name='customer_project_detail'),
    path('toggle-availability/', views.toggle_availability, name='toggle_availability'),
    path('check-availability/', views.check_availability, name='check_availability'),
    path('meeting/<int:meeting_id>/handle/', views.handle_meeting, name='handle_meeting'),
    path('meeting/<int:meeting_id>/join/', views.join_meeting, name='join_meeting'),
] 