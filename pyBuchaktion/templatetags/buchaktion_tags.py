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

@register.inclusion_tag('pyBuchaktion/tags/list_group_modules.html')
def list_group_modules(module_list):
    return {'modules': module_list}

@register.inclusion_tag('pyBuchaktion/tags/table_books.html')
def table_books(book_list):
    return {'books': book_list}

@register.inclusion_tag('pyBuchaktion/tags/dlist_book.html')
def dlist_book(book):
    return {'book': book}

@register.inclusion_tag('pyBuchaktion/tags/table_orders.html')
def table_orders(order_list, none_key='orders_none_found'):
    return {
        'orders': order_list,
        'none_key': none_key,
    }

@register.simple_tag()
def message(key, **kwargs):
    stuff = format_html(linebreaks(get_message(key)), **kwargs)
    return stuff
