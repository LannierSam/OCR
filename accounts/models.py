"""
Models for the accounts app.
Defines User, Student, and Landlord models.
"""

import uuid
import random
import string
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    """Custom manager for User model where email is the unique identifier."""
    use_in_migrations = True
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        
        # We don't use a separate username field
        extra_fields.setdefault('is_active', True)
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model with email as the unique identifier and role-based access."""
    
    # Custom service manager to bypass Django manager conflicts
    service = CustomUserManager()
    objects = CustomUserManager()
    
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('landlord', 'Landlord'),
        ('admin', 'Admin'),
    ]
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    
    # Authentication configuration
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    def __str__(self):
        return self.email
    
    @property
    def is_student(self):
        return self.role == 'student'
    
    @property
    def is_landlord(self):
        return self.role == 'landlord'
    
    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser


class Student(models.Model):
    """Student profile linked to User model."""
    
    LEVEL_CHOICES = [
        ('100', 'Level 100'),
        ('200', 'Level 200'),
        ('300', 'Level 300'),
        ('400', 'Level 400'),
       
    ]
    
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    
    student_id = models.CharField(max_length=20, unique=True, primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES)
    department = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(f"{self.first_name} {self.last_name} - {self.user.email}") # type: ignore
    
    def save(self, *args, **kwargs):
        if not self.student_id:
            # Generate student ID: STU-YEAR-XXXXXX
            year = timezone.now().year
            random_part = uuid.uuid4().hex[:6].upper()
            self.student_id = f"STU-{year}-{random_part}" # type: ignore
        super().save(*args, **kwargs)


class Landlord(models.Model):
    """Landlord profile linked to User model."""
    
    landlord_id = models.CharField(max_length=20, unique=True, primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='landlord_profile')
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    property_name = models.CharField(max_length=200, null=True, blank=True)
    property_location = models.CharField(max_length=255, null=True, blank=True)
    unique_code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.landlord_id:
            # Generate landlord ID: LL-8392-A7F
            part1 = "".join(random.choices(string.digits, k=4))
            part2 = "".join(random.choices(string.ascii_uppercase + string.digits, k=3))
            self.landlord_id = f"LL-{part1}-{part2}" # type: ignore
            
        if not self.unique_code:
            # Generate unique secure code for login: LL-XXXX
            random_code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
            self.unique_code = f"LL-{random_code}" # type: ignore
            
        super().save(*args, **kwargs)
    
    def __str__(self):
        return str(f"{self.full_name} ({self.landlord_id})") # type: ignore


class SentEmail(models.Model):
    """Model for logging sent emails for tracking and debugging."""
    objects = models.Manager()
    
    recipient = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(f"To: {self.recipient} | Subject: {self.subject} | Sent: {self.timestamp.strftime('%Y-%m-%d %H:%M')}") # type: ignore

