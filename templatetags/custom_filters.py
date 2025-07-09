
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """This filter will allow us to retrieve dictionary values by key."""
    return dictionary.get(key)
