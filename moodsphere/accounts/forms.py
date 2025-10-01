# accounts/forms.py
from django import forms
from .models import User

class UserRegistrationForm(forms.ModelForm):
    """Form for user registration"""
    
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm Password'
    }))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match")
        
        return cleaned_data


class UserLoginForm(forms.Form):
    """Form for user login"""
    
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username or Email'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))


class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile"""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'date_of_birth', 'bio', 'profile_image',
            'is_profile_public', 'allow_messages'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_profile_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'allow_messages': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }