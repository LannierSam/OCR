"""
URL configuration for properties app.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Student views
    path('properties/', views.property_list, name='property_list'),
    path('property/<int:property_id>/', views.property_detail, name='property_detail'),
    path('property/<int:property_id>/apply/', views.apply_property, name='apply_property'),
    path('property/<int:property_id>/review/', views.add_review, name='add_review'),
    path('applications/', views.student_applications, name='student_applications'),
    path('application/<int:application_id>/edit/', views.edit_application, name='edit_application_student'),
    path('application/<int:application_id>/delete/', views.delete_application, name='delete_application_student'),
    path('allocations/', views.student_allocations, name='student_allocations'),
    
    # Landlord views
    path('landlord/properties/', views.landlord_properties, name='landlord_properties'),
    path('landlord/property/add/', views.add_property, name='add_property'),
    path('landlord/property/<int:property_id>/edit/', views.edit_property, name='edit_property'),
    path('landlord/property/<int:property_id>/delete/', views.delete_property, name='delete_property'),
    path('landlord/applications/', views.landlord_applications, name='landlord_applications'),
    path('application/<int:application_id>/process/', views.process_application, name='process_application'),
    
    # Messaging
    path('messages/', views.messages_list, name='messages_list'),
    path('message/send/<int:user_id>/', views.send_message, name='send_message'),
    path('conversation/<int:user_id>/', views.conversation, name='conversation'),
]
