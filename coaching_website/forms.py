from django import forms
from .models import CoachingRequest, PricingPlan
from django.utils import timezone

class CoachingRequestForm(forms.ModelForm):

    plan = forms.ModelChoiceField(queryset=PricingPlan.objects.all(), widget=forms.HiddenInput(), required=False)
    class Meta:
        model = CoachingRequest
        fields = [
            'scheduled_datetime',
            'details',
            'name',
            'email',
            'phone',
            'referral_source',
            'plan'
        ]

        widgets = {
            'scheduled_datetime': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',  # Use datetime-local input for combined date and time
                    'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                    'placeholder': 'Select date & time',
                    # Add min attribute for 24 hours from now
                    'min': (timezone.now() + timezone.timedelta(hours=24)).strftime('%Y-%m-%dT%H:%M')

                },
                format='%Y-%m-%dT%H:%M'  # Format for datetime-local input
            ),
            'details': forms.Textarea(
                attrs={
                    'rows': '8',
                    'class': 'block p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                    'placeholder': 'Your details here'
                }
            ),
            'name': forms.TextInput(
                attrs={
                    'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                    'placeholder': 'Type your name'
                }
            ),
            'email': forms.EmailInput(
                attrs={
                    'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                    'placeholder': 'Type your email'
                }
            ),
            'phone': forms.TextInput(
                attrs={
                    'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                    'placeholder': 'Type your phone'
                }
            ),
            'referral_source': forms.Select(
                attrs={
                    'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'
                }
            ),
        }