from django.db import models
from django.core.validators import validate_email, RegexValidator
from django.utils import timezone


class CoachingRequest(models.Model):
    COACHING_NICHES = (
        ('life', 'Life'),
        ('business', 'Business'),
        ('dating', 'Dating'),
        ('health', 'Health'),
        ('career', 'Career'),
        ('other', 'Other'),
    )

    REVENUE_TARGETS = (
        ('5k-10k', '$5k - $10k / mo'),
        ('10k-20k', '$10k - $20k / mo'),
        ('20k-50k', '$20k - $50k / mo'),
        ('50k-100k+', '$50k - $100k+ / mo'),
    )

    ROADBLOCKS = (
        ('booking', 'Appointment Booking'),
        ('closing', 'Closing Sales'),
        ('retention', 'Client Retention'),
        ('time', 'Time'),
        ('other', 'Other'),
    )

    REFERRAL_SOURCES = (
        ('instagram', 'Instagram'),
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter'),
        ('facebook', 'Facebook'),
        ('other', 'Other'),
    )


    scheduled_datetime = models.DateTimeField("Date and Time", default=timezone.now) # Default to now, but allow changing
    details = models.TextField("Details", blank=True, null=True) 
    name = models.CharField("Name", max_length=255)
    email = models.EmailField("Email", validators=[validate_email])

    # Validate phone number to ensure a specific format if needed (e.g., US phone number)  
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone = models.CharField("Phone", validators=[phone_regex], max_length=17, blank=False)  # validators should be a list


    guests = models.IntegerField("Number of Guests", default=0) # Assuming guests can be 0 or more
    coaching_niche = models.CharField("Coaching Niche", max_length=10, choices=COACHING_NICHES)
    revenue_target = models.CharField("Revenue Target", max_length=10, choices=REVENUE_TARGETS)
    roadblock = models.CharField("Roadblock", max_length=10, choices=ROADBLOCKS)
    referral_source = models.CharField("Referral Source", max_length=10, choices=REFERRAL_SOURCES)


    created_at = models.DateTimeField(auto_now_add=True) # Automatically record creation time
    updated_at = models.DateTimeField(auto_now=True)  #Automatically update on each save


    def __str__(self):
        return f"Coaching Request from {self.name} on {self.scheduled_datetime}"


    class Meta:
        verbose_name = "Coaching Request"
        verbose_name_plural = "Coaching Requests"   
        ordering = ['-scheduled_datetime'] # Order by most recent requests first