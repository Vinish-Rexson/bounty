from django.urls import path
from . import views

app_name = 'customer'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('developers/', views.browse_developers, name='browse_developers'),
    path('developers/<int:dev_id>/', views.developer_profile, name='developer_profile'),
    path('projects/create/', views.create_project, name='create_project'),
    path('projects/<int:project_id>/requests/', views.project_requests, name='project_requests'),
    path('requests/<int:request_id>/handle/', views.handle_request, name='handle_request'),
    path('request-developer/<int:dev_id>/', views.request_developer, name='request_developer'),
] 