"""
Forms for the accounts app.
Includes registration forms for Student, Landlord, and authentication forms.
"""

from django import forms
from django.contrib.auth import get_user_model
from .models import Student, Landlord

User = get_user_model()


class UserLoginForm(forms.Form):
    """Form for user login with optional unique code for landlords."""
    
    email = forms.CharField(
        label='Email',
        widget=forms.TextInput(attrs={'class': 'block w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-blue-500', 'placeholder': 'Email'})
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'block w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-blue-500', 'placeholder': 'Password'})
    )
    unique_code = forms.CharField(
        label='Unique Code',
        required=False,
        widget=forms.TextInput(attrs={'class': 'block w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-blue-500', 'placeholder': 'LL-XXXXXX'})
    )


class StudentRegistrationForm(forms.ModelForm):
    """Form for student registration with email validation."""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Student Email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'})
    )
    
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'phone', 'level', 'department', 'gender']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'level': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Department'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean_email(self):
        """Validate student email domain and uniqueness."""
        email = self.cleaned_data.get('email', '').lower()
        if not (email.endswith('@hcuc.edu.gh')):
            raise forms.ValidationError("Please use a valid school email address (@hcuc.edu.gh)")
            
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered")
            
        return email
    
    def clean(self):
        """Validate password match."""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data


class StudentProfileForm(forms.ModelForm):
    """Form for student profile update."""
    
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'phone', 'level', 'department', 'gender']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'level': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
        }


class LandlordRegistrationForm(forms.ModelForm):
    """Form for landlord registration."""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'block w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-blue-500',
            'placeholder': 'Email Address'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'block w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-blue-500',
            'placeholder': '••••••••'
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'block w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-blue-500',
            'placeholder': '••••••••'
        })
    )
    
    class Meta:
        model = Landlord
        fields = ['full_name', 'phone', 'property_name', 'property_location']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'block w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Full Name',
                'autofocus': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'block w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Phone Number'
            }),
            'property_name': forms.TextInput(attrs={
                'class': 'block w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Property Name'
            }),
            'property_location': forms.TextInput(attrs={
                'class': 'block w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Property Location'
            }),
        }
    
    def clean_email(self):
        """Validate landlord email uniqueness."""
        email = self.cleaned_data.get('email', '').lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered")
        return email
    
    def clean(self):
        """Validate password match."""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data





class LandlordProfileForm(forms.ModelForm):
    """Form for landlord profile update."""
    
    class Meta:
        model = Landlord
        fields = ['full_name', 'phone']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

