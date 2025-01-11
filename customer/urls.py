from django.urls import path
from . import views

app_name = 'customer'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('developers/', views.browse_developers, name='browse_developers'),
    path('developers/<int:dev_id>/', views.developer_profile, name='developer_profile'),
    path('projects/create/', views.create_project, name='create_project'),
] 