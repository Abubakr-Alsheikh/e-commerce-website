from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings  # Import settings for email configuration
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils import timezone
from .forms import CoachingRequestForm  # Assuming your form is in forms.py


def index(request):
    return render(request, 'coaching/index.html')

def coaching_request_view(request):
    if request.method == 'POST':
        form = CoachingRequestForm(request.POST)
        if form.is_valid():
            
            scheduled_datetime = form.cleaned_data['scheduled_datetime']

            # Extract date and time components
            scheduled_date = scheduled_datetime.date()
            scheduled_time = scheduled_datetime.time()
            # scheduled_datetime = timezone.datetime.combine(scheduled_date, scheduled_time) #combine date and time into datetime object

            if scheduled_datetime <= timezone.now() + timezone.timedelta(hours=24):
                messages.error(request, 'Please select a date and time at least 24 hours in the future.')
            else:
                coaching_request = form.save()  # Save the form data to the database

                # Send email to the user
                # user_email = form.cleaned_data['email']
                # user_name = form.cleaned_data['name']
                # context = {
                #        'name': user_name,
                #        'scheduled_date':scheduled_date.strftime("%Y-%m-%d"),
                #        'scheduled_time': scheduled_time.strftime("%H:%M"), #format time for email
                #     }
                # subject = 'Your Coaching Request Confirmation'
                # html_message = render_to_string('emails/coaching_request_confirmation.html', context)
                # send_mail(subject, '', settings.DEFAULT_FROM_EMAIL,[user_email], html_message=html_message, fail_silently=False)


                # # Send email to the coach/admin
                # admin_email = settings.ADMIN_EMAIL  # Replace with your admin email
                # admin_context = {
                #        'name': user_name,
                #         'phone': form.cleaned_data['phone'],  
                #         'email':user_email,
                #         'scheduled_date': scheduled_date.strftime("%Y-%m-%d"),
                #         'scheduled_time': scheduled_time.strftime("%H:%M"),
                #         'coaching_niche': form.cleaned_data['coaching_niche'],
                #         'details':form.cleaned_data['details'],

                #        # Add other necessary context variables
                # }
                # admin_subject = f'New Coaching Request from {user_name}'
                # admin_html_message = render_to_string('emails/new_coaching_request_notification.html', admin_context)
                # send_mail(admin_subject, '', settings.DEFAULT_FROM_EMAIL, [admin_email], html_message=admin_html_message, fail_silently=False)


                messages.success(request, 'Your coaching request has been submitted successfully!')
                return redirect('coach:coaching_request')  # Redirect to a thank you page

    else:
        form = CoachingRequestForm()

    return render(request, 'coaching/coaching_request_form.html', {'form': form})