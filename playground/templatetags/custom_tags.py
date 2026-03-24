from django import template
import json

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, 0)

@register.filter
def times(number):
    return range(number)

@register.filter
def JSON_dump(obj):
    return json.dumps(obj)
