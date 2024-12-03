from django.db import models
from django.core.validators import validate_email, RegexValidator, MinValueValidator
from django.utils import timezone


class PricingPlan(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    sessions = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    featured = models.BooleanField(default=False, help_text="Mark this plan as featured.")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['price']  # Order plans by price ascending

class CoachingRequest(models.Model):
    REFERRAL_SOURCES = (
        ('instagram', 'Instagram'),
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter'),
        ('facebook', 'Facebook'),
        ('other', 'Other'),
    )


    scheduled_datetime = models.DateTimeField("Date and Time", default=timezone.now)
    details = models.TextField("Details", blank=True, null=True) 
    name = models.CharField("Name", max_length=255)
    email = models.EmailField("Email", validators=[validate_email])

    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone = models.CharField("Phone", validators=[phone_regex], max_length=17, blank=False)  # validators should be a list

    referral_source = models.CharField("Referral Source", max_length=10, choices=REFERRAL_SOURCES)
    plan = models.ForeignKey(PricingPlan, on_delete=models.SET_NULL, null=True, blank=True, related_name="coaching_requests")


    created_at = models.DateTimeField(auto_now_add=True) # Automatically record creation time
    updated_at = models.DateTimeField(auto_now=True)  #Automatically update on each save


    def __str__(self):
        return f"Coaching Request from {self.name} on {self.scheduled_datetime}"


    class Meta:
        verbose_name = "Coaching Request"
        verbose_name_plural = "Coaching Requests"
        ordering = ['-scheduled_datetime']
