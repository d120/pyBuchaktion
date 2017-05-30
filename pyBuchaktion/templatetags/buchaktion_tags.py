from django import template
from django.utils.html import linebreaks, format_html
from pyBuchaktion.messages import get_message

register = template.Library()

@register.inclusion_tag('pyBuchaktion/modulecategory.html')
def modulecategory_panel(name, module_list):
    return {
        'name': name,
        'module_list': module_list,
    }

@register.simple_tag()
def message(key, **kwargs):
    stuff = format_html(linebreaks(get_message(key)), **kwargs)
    return stuff
