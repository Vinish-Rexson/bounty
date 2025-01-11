from django.urls import path
from . import views

app_name = 'dev'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('home/', views.home, name='home'),
] 