from datetime import datetime

from django import template
from django.http import QueryDict
from django.utils.translation import ugettext_lazy as _

from pyBuchaktion.models import Book
from pyBuchaktion.data import net_library_csv

register = template.Library()

BOOK_STATE_CLASSES = {
    'AC': 'default',
    'RJ': 'danger',
    'PP': 'info',
    'OL': 'warning',
}

@register.filter
def get_state_class(state):
    return BOOK_STATE_CLASSES.get(state)

BOOK_STATE_TEXTS = {
    'AC': "",
    'RJ': _("This book has been rejected, and may not be ordered"),
    'PP': _("This book has been proposed, but has yet to be confirmed by our team. "
            "Orders may be posted but will not be proceeded with before confirmation. "
            "An order of a proposed book expresses your interest in it, and will increase "
            "the probability of it being confirmed."),
    'OL': _("This book has been marked obsolete, a new version is available. It may not be ordered"),
}

@register.filter
def get_state_text(state):
    return BOOK_STATE_TEXTS.get(state)

ORDER_STATUS_CLASSES = {
    'PD': 'info',
    'OD': 'success',
    'RJ': 'danger',
    'AR': 'info',
}

@register.filter
def get_status_class(status):
    return ORDER_STATUS_CLASSES.get(status)

ORDER_STATUS_TEXTS = {
    'PD': _("This book is marked for, but has not yet been ordered from our merchant. "
            "Until then, the order can be aborted at any time. We'll inform you when "
            "we ordered or finally rejected it."),
    'OD': _("This book has been ordered from our merchant. We'll inform you when it arrived."),
    'RJ': _("This order has been rejected."),
    'AR': _("The order was fulfilled, the book is now available."),
}

@register.filter
def get_status_text(status):
    return ORDER_STATUS_TEXTS.get(status)

@register.filter
def dict_unset(dct, key):
    _dct = dct.copy()
    if (key in _dct):
        _dct.pop(key)
    return _dct

@register.filter
def dict_join(value, param):
    dct = value.copy()
    for key, val in param.items():
        dct[key] = val
    return dct

@register.filter
def as_dict(value, param):
    return {param: value}

@register.filter
def form_as_dict(value):
    dct = QueryDict(mutable=True);
    for field in value:
        dct[field.name] = field.value()
    return dct

# This only works for QueryDicts!
@register.filter
def urlencode(value):
    return "?" + value.urlencode()

@register.inclusion_tag('pyBuchaktion/tags/list_limits.html')
def list_limits(data, params):
    lst = []
    dct = params.copy()
    page = int(dct.get('page', 1))
    index = (page - 1) * int(data['current'])

    for opt in data['options']:
        urldict = dct.copy()
        if opt == data['default']:
            if 'limit' in urldict:
                urldict.pop('limit')
        else:
            urldict['limit'] = opt

        newpage = (index // int(opt)) + 1
        if newpage > 1:
            urldict['page'] = newpage
        elif 'page' in urldict:
            urldict.pop('page')

        lst += [{
            'num': opt,
            'url': '?' + urldict.urlencode(),
        }]
    result = data.copy()
    result.update({
        'options': lst,
    })
    return result

@register.filter
def net_csv(queryset):
    return net_library_csv(queryset)

@register.simple_tag
def date():
    return datetime.now()
