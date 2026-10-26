"""
Views for the accounts app.
Handles authentication, registration, and dashboard routing.
"""

from django.shortcuts import render, redirect # type: ignore
from django.contrib.auth import login, logout, authenticate # type: ignore
from django.contrib.auth.decorators import login_required # type: ignore

from django.contrib import messages # type: ignore
from django.http import JsonResponse # type: ignore
from django.views.decorators.csrf import csrf_protect, csrf_exempt, ensure_csrf_cookie # type: ignore
from django.views.decorators.http import require_http_methods # type: ignore
from django.core.mail import send_mail # type: ignore
from django.conf import settings # type: ignore
import uuid
import random
import string

from .forms import (
    UserLoginForm,
    StudentRegistrationForm,
    StudentProfileForm,
    LandlordRegistrationForm,
    LandlordProfileForm,
)
from .models import User, Student, Landlord, SentEmail
from properties.models import Property, Application, Message


def send_landlord_code_email(landlord):
    """Send unique login code to landlord via email and log it."""
    subject = 'Your Landlord Login Code'
    message = f"""
Dear {landlord.full_name},

Your registration was successful.

Your unique login code is: {landlord.unique_code}

Use this code together with your email and password to log in.

Thank you.
    """
    recipient = landlord.user.email
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            fail_silently=False,
        )
        # Log the email
        SentEmail.objects.create( # type: ignore
            recipient=recipient,
            subject=subject,
            message=message
        )
        return True
    except Exception as e:
        # Log error for debugging
        import traceback
        error_msg = f"Error sending email to {recipient}: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)  # In production, use proper logging
        return False


def home(request):
    """Home page - redirects based on user role."""
    if request.user.is_authenticated:
        if Student.objects.filter(user=request.user).exists():
            return redirect('student_dashboard')
        elif Landlord.objects.filter(user=request.user).exists():
            return redirect('landlord_dashboard')
    return render(request, 'accounts/home.html')


def landing(request):
    """Landing page for unauthenticated users."""
    return render(request, 'accounts/landing.html')


@csrf_exempt
@ensure_csrf_cookie
@require_http_methods(["GET", "POST"])
def register(request):
    """Unified registration view for both students and landlords."""
    
    # Determine role from GET (for form display) or POST (for processing)
    role = request.GET.get('role', request.POST.get('role', 'student'))
    
    if request.method == 'POST':
        if role == 'student':
            form = StudentRegistrationForm(request.POST)
            if form.is_valid():
                # Create user with student role
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                
                # Create user
                user = User.service.create_user(
                    email=email,
                    password=password,
                    role='student'
                )
                
                # Create student profile (using cleaned_data)
                Student.objects.create( # type: ignore
                    user=user,
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    phone=form.cleaned_data['phone'],
                    level=form.cleaned_data['level'],
                    department=form.cleaned_data['department'],
                    gender=form.cleaned_data['gender']
                )
                
                messages.success(request, 'Registration successful! Please login to continue.')
                return redirect('login')
            else:
                # Form is invalid, fall through to render form with errors
                pass
        else:  # landlord
            form = LandlordRegistrationForm(request.POST)
            if form.is_valid():
                full_name = form.cleaned_data['full_name']
                email = form.cleaned_data['email']
                phone = form.cleaned_data['phone']
                property_name = form.cleaned_data['property_name']
                property_location = form.cleaned_data['property_location']
                password = form.cleaned_data['password']
                
                # Create user with landlord role
                user = User.service.create_user(
                    email=email,
                    password=password,
                    role='landlord'
                )
                
                # Create landlord profile (which auto-generates landlord_id)
                landlord = Landlord.objects.create( # type: ignore
                    user=user,
                    full_name=full_name,
                    phone=phone,
                    property_name=property_name,
                    property_location=property_location
                )
                
                # Send email code
                email_sent = send_landlord_code_email(landlord)
                
                if email_sent:
                    messages.success(request, 'Registration successful! A unique login code has been sent to your email. Please login to continue.')
                else:
                    messages.warning(request, 'Registration successful! However, we failed to send the login code to your email. Please check your email configuration or contact support.')
                return redirect('login')
            else:
                # Form is invalid, fall through to render form with errors
                pass
    else:
        if role == 'student':
            form = StudentRegistrationForm()
        else:
            form = LandlordRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form, 'role': role})


@require_http_methods(["GET", "POST"])
def student_register(request):
    """Student registration with email domain validation."""
    
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        
        if form.is_valid():
            # Create user with student role
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Create user
            user = User.service.create_user(
                email=email,
                password=password,
                role='student'
            )
            
            # Create student profile (using cleaned_data)
            Student.objects.create(
                user=user,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                phone=form.cleaned_data['phone'],
                level=form.cleaned_data['level'],
                department=form.cleaned_data['department'],
                gender=form.cleaned_data['gender']
            )
            
            # Auto-login after registration
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                messages.success(request, 'Registration successful! Welcome to the OCR Management System.')
                return redirect('home')
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'accounts/student_register.html', {'form': form})


@require_http_methods(["GET", "POST"])
def landlord_register(request):
    """Landlord registration with auto-generated landlord ID."""
    
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = LandlordRegistrationForm(request.POST)
        
        if form.is_valid():
            full_name = form.cleaned_data['full_name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            property_name = form.cleaned_data['property_name']
            property_location = form.cleaned_data['property_location']
            password = form.cleaned_data['password']
            
            # Create user with landlord role
            user = User.service.create_user(
                email=email,
                password=password,
                role='landlord'
            )
            
            # Create landlord profile (which auto-generates landlord_id)
            landlord = Landlord.objects.create(
                user=user,
                full_name=full_name,
                phone=phone,
                property_name=property_name,
                property_location=property_location
            )
            
            # Send email code
            email_sent = send_landlord_code_email(landlord)
            
            if email_sent:
                messages.success(request, 'Registration successful! A unique login code has been sent to your email. Please login to continue.')
            else:
                messages.warning(request, 'Registration successful! However, we failed to send the login code to your email. Please check your email configuration or contact support.')
            return redirect('login')
    else:
        form = LandlordRegistrationForm()
    
    return render(request, 'accounts/landlord_register.html', {'form': form})





@csrf_exempt
@ensure_csrf_cookie
@require_http_methods(["GET", "POST"])
def user_login(request):
    """General user login - routes based on role."""
    
    if request.user.is_authenticated:
        return redirect('landing')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        role = request.POST.get('role', 'student')
        
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            if role == 'student':
                student_email = email.lower()
                user = authenticate(request, username=student_email, password=password)
                
                if user is not None and Student.objects.filter(user=user).exists():
                    login(request, user)
                    messages.success(request, f'Welcome back!')
                    return redirect('home')
                else:
                    messages.error(request, 'Invalid email or password.')
            else:
                # Landlord login - requires unique code
                user = authenticate(request, username=email, password=password)
                unique_code = form.cleaned_data.get('unique_code')
                
                landlord_profile = Landlord.objects.filter(user=user).first()
                if user is not None and landlord_profile:
                    if landlord_profile.unique_code == unique_code:
                        login(request, user)
                        messages.success(request, f'Welcome back!')
                        return redirect('home')
                    else:
                        messages.error(request, 'Invalid unique code.')
                else:
                    messages.error(request, 'Invalid email or password.')
    else:
        form = UserLoginForm()
        role = 'student'
    
    return render(request, 'accounts/login.html', {
        'form': form,
        'selected_role': role
    })


@ensure_csrf_cookie
@require_http_methods(["GET", "POST"])
def landlord_login(request):
    """Landlord login using email and password."""
    
    if request.user.is_authenticated and Landlord.objects.filter(user=request.user).exists():
        return redirect('landlord_dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            unique_code = form.cleaned_data.get('unique_code')
            
            landlord_profile = Landlord.objects.filter(user=user).first()
            if user is not None and landlord_profile:
                if landlord_profile.unique_code == unique_code:
                    login(request, user)
                    messages.success(request, 'Login successful!')
                    return redirect('landlord_dashboard')
                else:
                    messages.error(request, 'Invalid unique code.')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/landlord_login.html', {'form': form})


@login_required
def user_logout(request):
    """User logout."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('landing')


@login_required
def student_dashboard(request):
    """Student dashboard with property search."""
    if not Student.objects.filter(user=request.user).exists():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    student = Student.objects.get(user=request.user)
    
    # Get all approved properties with media and landlord profiles prefetched
    from properties.models import Property
    latest_properties = Property.objects.all().prefetch_related('media_files', 'landlord__landlord_profile').order_by('-created_at')
    
    # Dashboard stats
    stats = {
        'total_applications': Application.objects.filter(student=request.user).count(),
        'approved_applications': Application.objects.filter(student=request.user, status='approved').count(),
        'pending_applications': Application.objects.filter(student=request.user, status='pending').count(),
        'unread_messages': Message.objects.filter(receiver_user=request.user, is_read=False).count(),
    }
    
    return render(request, 'accounts/student_dashboard.html', {
        'student': student,
        'latest_properties': latest_properties,
        'stats': stats
    })


@login_required
def landlord_dashboard(request):
    """Landlord dashboard with property management."""
    if request.user.role != 'landlord':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    landlord = Landlord.objects.get(user=request.user)
    
    # Dashboard stats
    stats = {
        'total_properties': Property.objects.filter(landlord=request.user).count(),
        'total_applications': Application.objects.filter(property__landlord=request.user).count(),
        'pending_applications': Application.objects.filter(property__landlord=request.user, status='pending').count(),
        'unread_messages': Message.objects.filter(receiver_user=request.user, is_read=False).count(),
    }
    
    return render(request, 'accounts/landlord_dashboard.html', {
        'landlord': landlord,
        'stats': stats
    })





@login_required
def student_profile(request):
    """Student profile update."""
    if request.user.role != 'student':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    student = Student.objects.get(user=request.user)
    
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('student_profile')
    else:
        form = StudentProfileForm(instance=student)
    
    return render(request, 'accounts/student_profile.html', {'form': form, 'student': student})


@login_required
def landlord_profile(request):
    """Landlord profile update."""
    if not Landlord.objects.filter(user=request.user).exists():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    landlord = Landlord.objects.get(user=request.user)
    
    if request.method == 'POST':
        form = LandlordProfileForm(request.POST, instance=landlord)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('landlord_profile')
    else:
        form = LandlordProfileForm(instance=landlord)
    
    return render(request, 'accounts/landlord_profile.html', {
        'form': form,
        'landlord': landlord,
        'unique_code': landlord.unique_code
    })


@login_required
def verify_code(request):
    """View for verifying landlord's unique code."""
    if not Landlord.objects.filter(user=request.user).exists():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    landlord = Landlord.objects.get(user=request.user)
    
    if request.method == 'POST':
        # TODO: Add verification logic
        entered_code = request.POST.get('unique_code')
        if entered_code == landlord.unique_code:
            landlord.is_verified = True
            landlord.save()
            messages.success(request, 'Code verified successfully!')
            return redirect('landlord_dashboard')
        else:
            messages.error(request, 'Invalid code. Please try again.')
    
    return render(request, 'accounts/verify_code.html', {
        'landlord': landlord
    })
