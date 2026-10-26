"""
Views for the properties app.
Handles property management, applications, reviews, and messaging.
"""

from django.shortcuts import render, redirect, get_object_or_404 # type: ignore
from django.contrib.auth.decorators import login_required # type: ignore
from django.contrib import messages # type: ignore
from django.contrib.auth import get_user_model # type: ignore
from django.db.models import Q # type: ignore
from django.http import JsonResponse # type: ignore
from django.views.decorators.csrf import csrf_protect # type: ignore
from django.views.decorators.http import require_http_methods # type: ignore


from .models import Property, Application, Allocation, Review, Message, PropertyMedia
from .forms import PropertyForm, ApplicationForm, ReviewForm, MessageForm, PropertySearchForm
from accounts.models import Student, Landlord

User = get_user_model()


# ==================== STUDENT VIEWS ====================

@login_required
def property_list(request):
    """List all approved properties with search and filters."""
    if not request.user.is_student:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    properties = Property.objects.all().prefetch_related('media_files', 'landlord__landlord_profile')
    
    # Apply filters
    search = request.GET.get('search', '')
    room_type = request.GET.get('room_type', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    
    if search:
        properties = properties.filter(
            Q(property_name__icontains=search) | # type: ignore
            Q(location__icontains=search) |      # type: ignore
            Q(description__icontains=search)     # type: ignore
        )
    
    if room_type:
        properties = properties.filter(room_type=room_type)
    
    if min_price:
        properties = properties.filter(price__gte=min_price)
    
    if max_price:
        properties = properties.filter(price__lte=max_price)
    
    form = PropertySearchForm(request.GET)
    
    return render(request, 'properties/property_list.html', {
        'properties': properties,
        'form': form,
    })


@login_required
def property_detail(request, property_id):
    """View property details."""
    if not request.user.is_student:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    property = get_object_or_404(Property, pk=property_id)
    reviews = property.reviews.all()[:10]
    
    # Check if user has already applied
    existing_application = Application.objects.filter(
        student=request.user,
        property=property
    ).first()
    
    # Check if already allocated
    allocation = Allocation.objects.filter(student=request.user, property=property, is_active=True).first()
    
    return render(request, 'properties/property_detail.html', {
        'property': property,
        'reviews': reviews,
        'existing_application': existing_application,
        'allocation': allocation,
        'review_form': ReviewForm(),
    })


@login_required
@csrf_protect
@require_http_methods(["GET", "POST"])
def apply_property(request, property_id):
    """Apply for accommodation."""
    if not request.user.is_student:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    property_obj = get_object_or_404(Property, pk=property_id)
    
    # Check if already applied
    existing = Application.objects.filter(student=request.user, property=property_obj).first()
    if existing:
        messages.info(request, 'You have already applied for this property.')
        return redirect('property_detail', property_id=property_id)
    
    # Check availability
    if property_obj.available_rooms <= 0:
        messages.error(request, 'No rooms available.')
        return redirect('property_detail', property_id=property_id)
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.student = request.user
            application.property = property_obj
            application.save()
            messages.success(request, 'Application submitted successfully!')
            return redirect('student_applications')
    else:
        form = ApplicationForm()
    
    return render(request, 'properties/apply_property.html', {
        'form': form,
        'property': property_obj,
    })


@login_required
def student_applications(request):
    """View student's applications."""
    if not request.user.is_student:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    applications = Application.objects.filter(student=request.user)
    
    return render(request, 'properties/student_applications.html', {
        'applications': applications,
    })


@login_required
@csrf_protect
@require_http_methods(["GET", "POST"])
def edit_application(request, application_id):
    """Edit an existing application."""
    if not request.user.is_student:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    application = get_object_or_404(Application, pk=application_id)
    
    # Check ownership
    if application.student != request.user:
        messages.error(request, 'Access denied.')
        return redirect('student_applications')
    
    # Can only edit pending applications
    if application.status != 'pending':
        messages.error(request, 'You cannot edit an application that has already been processed.')
        return redirect('student_applications')
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, 'Application updated successfully!')
            return redirect('student_applications')
    else:
        form = ApplicationForm(instance=application)
    
    return render(request, 'properties/edit_application.html', {
        'form': form,
        'application': application,
        'property': application.property,
    })


@login_required
def delete_application(request, application_id):
    """Delete (withdraw) an application."""
    if not request.user.is_student:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    application = get_object_or_404(Application, pk=application_id)
    
    # Check ownership
    if application.student != request.user:
        messages.error(request, 'Access denied.')
        return redirect('student_applications')
    
    # If approved, we need to add the room back
    if application.status == 'approved':
        property_obj = application.property
        property_obj.available_rooms += 1
        property_obj.save()
    
    application.delete()
    messages.success(request, 'Application withdrawn successfully.')
    return redirect('student_applications')


@login_required
def student_allocations(request):
    """View student's allocations."""
    if not request.user.is_student:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    allocations = Allocation.objects.filter(student=request.user, is_active=True)
    
    return render(request, 'properties/student_allocations.html', {
        'allocations': allocations,
    })


@login_required
def add_review(request, property_id):
    """Add a review to a property."""
    if not request.user.is_student:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    property_obj = get_object_or_404(Property, pk=property_id)
    
    # Check if already reviewed
    existing = Review.objects.filter(student=request.user, property=property_obj).first()
    if existing:
        messages.info(request, 'You have already reviewed this property.')
        return redirect('property_detail', property_id=property_id)
    
    # Check if student was allocated to this property
    allocation = Allocation.objects.filter(student=request.user, property=property_obj, is_active=True).first()
    if not allocation:
        messages.error(request, 'You can only review properties you have been allocated to.')
        return redirect('property_detail', property_id=property_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.student = request.user
            review.property = property_obj
            review.save()
            messages.success(request, 'Review submitted!')
            return redirect('property_detail', property_id=property_id)
    else:
        form = ReviewForm()
    
    return render(request, 'properties/add_review.html', {
        'form': form,
        'property': property_obj,
    })


# ==================== LANDLORD VIEWS ====================

@login_required
def landlord_properties(request):
    """View landlord's properties."""
    if not request.user.is_landlord:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    properties = Property.objects.filter(landlord=request.user)
    
    return render(request, 'properties/landlord_properties.html', {
        'properties': properties,
    })


@login_required
@csrf_protect
@require_http_methods(["GET", "POST"])
def add_property(request):
    """Add a new property listing."""
    if not request.user.is_landlord:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property = form.save(commit=False)
            property.landlord = request.user
            
            # Handle multiple media files properly
            files = request.FILES.getlist('image')
            if files:
                # First file goes to the main property image
                property.image = files[0]
            property.save()
            
            # If more files are uploaded, add them to PropertyMedia
            if len(files) > 1:
                for f in files[1:]:
                    PropertyMedia.objects.create(property=property, file=f)
                
            messages.success(request, 'Property added successfully! Pending approval.')
            return redirect('landlord_properties')
    else:
        form = PropertyForm()
    
    return render(request, 'properties/add_property.html', {'form': form})


@login_required
@csrf_protect
@require_http_methods(["GET", "POST"])
def edit_property(request, property_id):
    """Edit a property listing."""
    if not request.user.is_landlord:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    property = get_object_or_404(Property, pk=property_id)
    
    # Check ownership
    if property.landlord != request.user:
        messages.error(request, 'Access denied.')
        return redirect('landlord_properties')
    
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property)
        if form.is_valid():
            # Check if new files were uploaded
            files = request.FILES.getlist('image')
            
            if files:
                # If new images are uploaded, we assume the landlord wants to replace the gallery
                # Clear existing media files to ensure "all new" images are shown
                property.media_files.all().delete()
                
                # Set the first file as the main image
                property.image = files[0]
                
                # Save the property first
                property.save()
                
                # Save additional images to PropertyMedia
                if len(files) > 1:
                    for f in files[1:]:
                        PropertyMedia.objects.create(property=property, file=f)
            else:
                # No new images uploaded, just save the other fields
                property = form.save()
                    
            messages.success(request, 'Property updated successfully!')
            return redirect('landlord_properties')
    else:
        form = PropertyForm(instance=property)
    
    return render(request, 'properties/edit_property.html', {
        'form': form,
        'property': property,
    })


@login_required
def delete_property(request, property_id):
    """Delete a property listing."""
    if not request.user.is_landlord:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    property = get_object_or_404(Property, pk=property_id)
    
    # Check ownership
    if property.landlord != request.user:
        messages.error(request, 'Access denied.')
        return redirect('landlord_properties')
    
    property.delete()
    messages.success(request, 'Property deleted successfully!')
    return redirect('landlord_properties')


@login_required
def landlord_applications(request):
    """View applications for landlord's properties."""
    if not request.user.is_landlord:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    properties = Property.objects.filter(landlord=request.user).values_list('property_id', flat=True)
    applications = Application.objects.filter(property__in=properties)
    
    return render(request, 'properties/landlord_applications.html', {
        'applications': applications,
    })


@login_required
@require_http_methods(["POST"])
def process_application(request, application_id):
    """Approve or reject an application."""
    if not request.user.is_landlord:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    application = get_object_or_404(Application, pk=application_id)
    
    # Check ownership
    if application.property.landlord != request.user:
        messages.error(request, 'Access denied.')
        return redirect('landlord_applications')
    
    action = request.POST.get('action', '')
    notes = request.POST.get('notes', '')
    
    if action == 'approve':
        # Check room availability
        if application.property.available_rooms > 0:
            application.status = 'approved'
            application.admin_notes = notes
            application.save()
            
            # Decrease available rooms
            property = application.property
            property.available_rooms -= 1
            property.save()
            
            messages.success(request, 'Application approved!')
        else:
            messages.error(request, 'No rooms available.')
    elif action == 'reject':
        application.status = 'rejected'
        application.admin_notes = notes
        application.save()
        messages.success(request, 'Application rejected.')
    
    return redirect('landlord_applications')


# ==================== MESSAGING ====================

@login_required
def messages_list(request):
    """View all messages."""
    conversations = get_user_conversations(request.user)
    return render(request, 'properties/messages_list.html', {
        'conversations': conversations,
    })


@login_required
@csrf_protect
@require_http_methods(["GET", "POST"])
def send_message(request, user_id):
    """Send a message to another user."""
    receiver = get_object_or_404(User, pk=user_id)
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender_user = request.user
            message.receiver_user = receiver
            message.save()
            messages.success(request, 'Message sent!')
            return redirect('conversation', user_id=user_id)
    else:
        form = MessageForm()
    
    return render(request, 'properties/send_message.html', {
        'form': form,
        'receiver': receiver,
    })


@login_required
def conversation(request, user_id):
    """View conversation with another user."""
    other_user = get_object_or_404(User, pk=user_id)
    conversations = get_user_conversations(request.user)
    
    # Get messages
    messages = Message.objects.filter(
        (Q(sender_user=request.user) & Q(receiver_user=other_user)) |  # type: ignore
        (Q(sender_user=other_user) & Q(receiver_user=request.user))    # type: ignore
    ).order_by('timestamp')
    
    # Mark as read
    messages.filter(receiver_user=request.user, is_read=False).update(is_read=True)
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender_user = request.user
            message.receiver_user = other_user
            message.save()
            return redirect('conversation', user_id=user_id)
    else:
        form = MessageForm()
    
    return render(request, 'properties/conversation.html', {
        'other_user': other_user,
        'messages': messages,
        'form': form,
        'conversations': conversations,
    })


def get_user_conversations(user):
    """Helper to get all conversations for a user."""
    messages_list = Message.objects.filter(
        Q(sender_user=user) | Q(receiver_user=user) # type: ignore
    ).order_by('-timestamp')
    
    conversations = {}
    for msg in messages_list:
        other_user = msg.receiver_user if msg.sender_user == user else msg.sender_user
        if other_user.id not in conversations:
            conversations[other_user.id] = {
                'user': other_user,
                'last_message': msg,
                'unread': 0
            }
        if not msg.is_read and msg.receiver_user == user:
            conversations[other_user.id]['unread'] += 1
            
    # Sort conversations by the timestamp of the last message (most recent first)
    sorted_conversations = sorted(
        conversations.values(),
        key=lambda x: x['last_message'].timestamp,
        reverse=True
    )
    return sorted_conversations



