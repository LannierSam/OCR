"""
URL configuration for accounts app.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('home/', views.home, name='home'),
    
    # Authentication
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Student
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/profile/', views.student_profile, name='student_profile'),
    path('student/register/', views.student_register, name='student_register'),
    
    # Landlord
    path('landlord/login/', views.landlord_login, name='landlord_login'),
    path('landlord/dashboard/', views.landlord_dashboard, name='landlord_dashboard'),
    path('landlord/profile/', views.landlord_profile, name='landlord_profile'),
    path('landlord/register/', views.landlord_register, name='landlord_register'),
    path('landlord/verify/', views.verify_code, name='verify_code'),
    
    # Unified registration
    path('register/', views.register, name='register'),
    
    # Admin - using Django default admin at /admin/
]
