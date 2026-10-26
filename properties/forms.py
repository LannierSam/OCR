"""
Forms for the properties app.
Includes forms for Property, Application, Review, and Message.
"""

from django import forms
from django.core.exceptions import ValidationError
from .models import Property, Application, Review, Message


class PropertyForm(forms.ModelForm):
    """Form for creating/editing property listings."""
    
    class Meta:
        model = Property
        fields = [
            'property_name', 'location', 'room_type', 'price',
            'total_rooms', 'available_rooms', 'description',
            'facilities', 'image'
        ]
        widgets = {
            'property_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Property Name'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location/Address'}),
            'room_type': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price per month'}),
            'total_rooms': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Total rooms'}),
            'available_rooms': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Available rooms'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description', 'rows': 4}),
            'facilities': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Facilities', 'rows': 2}),
        }
    
    def clean(self):
        """Validate room counts."""
        cleaned_data = super().clean() or self.cleaned_data
        total_rooms = cleaned_data.get('total_rooms', 0)
        available_rooms = cleaned_data.get('available_rooms', 0)
        
        if total_rooms < 1:
            raise ValidationError('Total rooms must be at least 1.')
        
        if available_rooms < 0:
            raise ValidationError('Available rooms cannot be negative.')
        
        if available_rooms > total_rooms:
            raise ValidationError('Available rooms cannot exceed total rooms.')
        
        return cleaned_data


class ApplicationForm(forms.ModelForm):
    """Form for applying to a property."""
    
    class Meta:
        model = Application
        fields = ['full_name', 'phone', 'move_in_date', 'duration', 'additional_info']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition',
                'placeholder': 'Enter your full name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition',
                'placeholder': 'Enter phone number'
            }),
            'move_in_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition',
                'type': 'date'
            }),
            'duration': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition',
                'placeholder': '12'
            }),
            'additional_info': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition',
                'placeholder': 'Any additional information...',
                'rows': 4
            }),
        }


class ReviewForm(forms.ModelForm):
    """Form for submitting a property review."""
    
    class Meta:
        model = Review
        fields = ['rating', 'comment', 'pros', 'cons']
        widgets = {
            'rating': forms.HiddenInput(),
            'comment': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition',
                'placeholder': 'Your review (optional)',
                'rows': 4
            }),
            'pros': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition',
                'placeholder': 'Pros (optional)'
            }),
            'cons': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition',
                'placeholder': 'Cons (optional)'
            }),
        }


class MessageForm(forms.ModelForm):
    """Form for sending messages."""
    
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Type your message...',
                'rows': 4
            }),
        }


class PropertySearchForm(forms.Form):
    """Form for searching and filtering properties."""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search properties...'
        })
    )
    room_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Room Types')] + list(Property.ROOM_TYPE_CHOICES),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    min_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Price'
        })
    )
    max_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max Price'
        })
    )
    available_only = forms.BooleanField(
        required=False,
        label='Available only',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
