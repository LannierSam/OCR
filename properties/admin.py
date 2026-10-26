"""
Admin configuration for properties app.
"""

from django.contrib import admin
from .models import Property, Application, Allocation, Review, Message


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    """Admin for Property model."""
    
    list_display = ['property_name', 'landlord', 'location', 'room_type', 'price', 'available_rooms', 'approval_status', 'created_at']
    list_filter = ['room_type', 'approval_status', 'created_at']
    search_fields = ['property_name', 'location', 'landlord__full_name']
    raw_id_fields = ['landlord']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['approval_status']


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    """Admin for Application model."""
    
    list_display = ['student', 'property', 'application_date', 'status']
    list_filter = ['status', 'application_date']
    search_fields = ['student__user__email', 'property__property_name']
    raw_id_fields = ['student', 'property']
    readonly_fields = ['application_date']


@admin.register(Allocation)
class AllocationAdmin(admin.ModelAdmin):
    """Admin for Allocation model."""
    
    list_display = ['student', 'property', 'room_number', 'allocation_date']
    list_filter = ['allocation_date']
    search_fields = ['student__user__email', 'property__property_name', 'room_number']
    raw_id_fields = ['student', 'property']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin for Review model."""
    
    list_display = ['property', 'student', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['property__property_name', 'student__user__email']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin for Message model."""
    
    list_display = ['sender_user', 'receiver_user', 'property', 'timestamp', 'is_read']
    list_filter = ['is_read', 'timestamp']
    search_fields = ['sender_user__email', 'receiver_user__email', 'content']
    readonly_fields = ['timestamp']
