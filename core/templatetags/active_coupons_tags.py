from django import template
from core.models import Coupon
from django.utils import timezone

register = template.Library()

@register.simple_tag
def get_active_coupons():
    return Coupon.objects.filter(active=True, valid_from__lte=timezone.now(), valid_to__gte=timezone.now())