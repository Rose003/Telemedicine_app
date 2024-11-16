from django import template
import json


register = template.Library()

@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key, [])
    return []

@register.filter
def to_json(value):
    return json.dumps(value)
