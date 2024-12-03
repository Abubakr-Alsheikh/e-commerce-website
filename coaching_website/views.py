from django.shortcuts import get_object_or_404, render, redirect
from django.core.mail import send_mail
from django.conf import settings  # Import settings for email configuration
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils import timezone

from .models import PricingPlan
from .forms import CoachingRequestForm


def index(request):
    plans = PricingPlan.objects.all()
    return render(request, 'coaching/index.html', {'plans': plans})

def coaching_request_view(request, plan_id):
    try:
        plan = get_object_or_404(PricingPlan, pk=plan_id)
    except PricingPlan.DoesNotExist:
        messages.error(request, "Invalid plan selected.")
        return redirect('coaching:index') # Redirect to the index page or another appropriate page

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

                coaching_request = form.save(commit=False) # Don't save yet
                coaching_request.plan = plan

                coaching_request.save() # Now save
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


                messages.success(request, 'Your coaching request has been submitted successfully, wait until we contact you!')
                return redirect('coaching:index')

    else:
        try:
            selected_plan = PricingPlan.objects.get(pk=plan_id) # Get plan for initial form
            form = CoachingRequestForm(initial={'plan': selected_plan})  # Pre-select the plan
        except PricingPlan.DoesNotExist:
             form = CoachingRequestForm()

    return render(request, 'coaching/coaching_request_form.html', {'form': form, 'plan': plan})