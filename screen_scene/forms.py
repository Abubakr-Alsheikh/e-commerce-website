from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ('username', 'email')  # Add 'email' if you want

class CustomAuthenticationForm(AuthenticationForm):
    # Add custom fields or styling if needed
    pass