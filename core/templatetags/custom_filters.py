from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
def to(value, end):
    return range(value, end + 1)

@register.filter
def downto(value, end):
    return range(value, end - 1, -1)

@register.filter
@stringfilter
def get_item(dictionary, key):
    """Retrieve value from a dictionary using a key."""
    return dictionary.get(key, '')

# Usage in template: {{ my_dict|get:"my_key" }}

@register.filter
@stringfilter
def add(value, arg):
    """Concatenate value and arg."""
    return f"{value}{arg}"

# Usage in template: {{ my_value|add:"my_suffix" }}