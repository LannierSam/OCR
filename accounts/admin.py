"""
Admin configuration for accounts app.
"""

from django.contrib import admin
from .models import User, Student, Landlord, SentEmail


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Custom admin for User model."""
    
    list_display = ['email', 'role', 'is_active', 'is_staff', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['email']
    ordering = ['-date_joined']
    readonly_fields = ['date_joined', 'last_login']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Role', {'fields': ('role',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role'),
        }),
    )


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Admin for Student model."""
    
    list_display = ['student_id', 'first_name', 'last_name', 'user', 'level', 'department', 'created_at']
    list_filter = ['level', 'gender', 'created_at']
    search_fields = ['student_id', 'first_name', 'last_name', 'user__email', 'department']
    raw_id_fields = ['user']
    readonly_fields = ['student_id', 'created_at', 'updated_at']


@admin.register(Landlord)
class LandlordAdmin(admin.ModelAdmin):
    """Admin for Landlord model."""
    
    list_display = ['landlord_id', 'full_name', 'user', 'phone', 'unique_code', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['landlord_id', 'full_name', 'user__email', 'unique_code', 'property_name', 'property_location']
    raw_id_fields = ['user']
    readonly_fields = ['landlord_id', 'unique_code', 'created_at']


@admin.register(SentEmail)
class SentEmailAdmin(admin.ModelAdmin):
    """Admin for SentEmail log model."""
    
    list_display = ['recipient', 'subject', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['recipient', 'subject', 'message']
    readonly_fields = ['recipient', 'subject', 'message', 'timestamp']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
