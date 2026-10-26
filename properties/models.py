"""
Models for the properties app.
Defines Property, Application, Allocation, Review, and Message models.
"""

from django.db import models # type: ignore
from django.conf import settings # type: ignore

# Import from accounts app
from accounts.models import Student, Landlord
import builtins


class Property(models.Model):
    """Property listing model."""
    objects = models.Manager()
    
    ROOM_TYPE_CHOICES = [
        ('single', 'Single Room'),
        ('double', 'Double Room'),
        ('shared', 'Shared Room'),
        ('self_contained', 'Self-Contained'),
    ]
    
    APPROVAL_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    property_id = models.AutoField(primary_key=True)
    landlord = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='properties')
    property_name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_rooms = models.PositiveIntegerField()
    available_rooms = models.PositiveIntegerField()
    description = models.TextField()
    facilities = models.TextField(null=True, blank=True)
    image = models.FileField(upload_to='property_images/', null=True, blank=True)
    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.property_name)

    @property
    def is_video(self):
        if self.image:
            ext = str(self.image.name).lower().split('.')[-1]
            return ext in ['mp4', 'mov', 'avi', 'mkv', 'webm']
        return False

    @property
    def get_thumbnail(self):
        """Returns the main image URL or falls back to the first media file."""
        if self.image:
            try:
                return self.image.url
            except (ValueError, AttributeError):
                pass
        
        # Fallback to the first media file using the related manager
        # This respects prefetch_related and is more efficient
        first_media = self.media_files.all().order_by('id').first()
        if first_media and first_media.file:
            try:
                return first_media.file.url
            except (ValueError, AttributeError):
                return None
        return None

    @property
    def thumbnail_is_video(self):
        """Checks if the thumbnail is a video."""
        url = self.get_thumbnail
        if url:
            ext = str(url).lower().split('.')[-1]
            return ext in ['mp4', 'mov', 'avi', 'mkv', 'webm']
        return False

    @property
    def id(self):
        return self.property_id


class PropertyMedia(models.Model):
    """Additional media files (images/videos) for a property."""
    objects = models.Manager()
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='media_files')
    file = models.FileField(upload_to='property_media/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    @builtins.property
    def is_video(self):
        if self.file:
            ext = str(self.file.name).lower().split('.')[-1]
            return ext in ['mp4', 'mov', 'avi', 'mkv', 'webm']
        return False


class Application(models.Model):
    """Student application for accommodation."""
    objects = models.Manager()
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    application_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='applications')
    
    # New Application Fields
    full_name = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    move_in_date = models.DateField(null=True, blank=True)
    duration = models.IntegerField(default=12, help_text="Duration in months")
    additional_info = models.TextField(null=True, blank=True)
    
    application_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return str(f"Application by {self.student} for {self.property}")

    @builtins.property
    def id(self):
        return self.application_id


class Allocation(models.Model):
    """Room allocation to student."""
    objects = models.Manager()
    
    allocation_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='allocations')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='allocations')
    room_number = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    allocation_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(f"Allocation for {self.student} in {self.property}")

    @builtins.property
    def id(self):
        return self.allocation_id


class Review(models.Model):
    """Property review by student."""
    objects = models.Manager()
    
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    pros = models.CharField(max_length=255, null=True, blank=True)
    cons = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(f"Review by {self.student} for {self.property}")


class Message(models.Model):
    """Messaging system between students and landlords."""
    objects = models.Manager()
    
    sender_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    receiver_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_messages'
    )
    property = models.ForeignKey(Property, on_delete=models.CASCADE, null=True, blank=True, related_name='messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return str(f"Message from {self.sender_user} to {self.receiver_user}")
