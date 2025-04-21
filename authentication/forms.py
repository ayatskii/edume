from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class UserRegistrationForm(UserCreationForm):
    """Form for user registration with role selection"""
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
        }

class UserProfileForm(forms.ModelForm):
    """Form for updating user profile information"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'bio', 'avatar']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

class NotificationPreferencesForm(forms.ModelForm):
    """Form for updating notification preferences"""
    class Meta:
        model = User
        fields = ['email_notifications', 'push_notifications']
        labels = {
            'email_notifications': 'Receive email notifications',
            'push_notifications': 'Receive browser notifications',
        } 