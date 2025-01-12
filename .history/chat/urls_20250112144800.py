from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_list, name='list'),
    path('create/', views.create_room, name='create_room'),
    path('<int:room_id>/', views.chat_room, name='room'),
    path('project/<int:project_id>/request-status/', views.request_project_status, name='request_project_status'),
    path('project/<int:project_id>/approve-status/', views.approve_status_request, name='approve_status_request'),
]
