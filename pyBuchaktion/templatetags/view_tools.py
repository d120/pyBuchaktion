from pyBuchaktion.models import Book
from django import template
from django.utils.translation import ugettext_lazy as _

register = template.Library()

BOOK_STATE_CLASSES = [
    ('AC', 'default'),
    ('RJ', 'danger'),
    ('PP', 'info'),
    ('OL', 'warning'),
]

def get_state_class(state):
    return [(s, v) for s, v in BOOK_STATE_CLASSES if s == state][0][1]


BOOK_STATE_TEXTS = [
    ('AC', ""),
    ('RJ', _("This book has been rejected, and may not be ordered")),
    ('PP', _("This book has been proposed, but has yet to be confirmed by our team. "
        "Until then it may not be ordered.")),
    ('OL', _("This book has been marked obsolete, a new version is available. It may not be ordered")),    
]

def get_state_text(state):
    return [(s, t) for s, t in BOOK_STATE_TEXTS if s == state][0][1]

ORDER_STATUS_CLASSES = [
    ('PD', 'info'),
    ('OD', 'success'),
    ('RJ', 'danger'),
    ('AR', 'info'),
]

def get_status_class(status):
    return [(s, v) for s, v in ORDER_STATUS_CLASSES if s == status][0][1]


ORDER_STATUS_TEXTS = [
    ('PD', _("This book is marked for, but has not yet been ordered from our merchant. "
        "Until then, the order can be aborted at any time. We'll inform you when we ordered "
        "or finally rejected it.")),
    ('OD', _("This book has been ordered from our merchant. We'll inform you when it arrived.")),
    ('RJ', _("This order has been rejected.")),
    ('AR', _("The order was fulfilled, the book is now available.")),
]

def get_status_text(status):
    return [(s, t) for s, t in ORDER_STATUS_TEXTS if s == status][0][1]

register.filter('get_state_class', get_state_class)
register.filter('get_state_text', get_state_text)

register.filter('get_status_class', get_status_class)
register.filter('get_status_text', get_status_text)


@register.inclusion_tag('url.html')
def url_set(params, key, value, drop = None):
    params_ = params.copy()
    params_[key] = value

    if (drop != None and drop in params_):
        params_.pop(drop)

    url = "?" + params_.urlencode()
    return {"url": url}

@register.inclusion_tag('url.html')
def url_unset(params, key):
    params_ = params.copy()
    if key in params_:
        params_.pop(key)
    
    # always return at least '?' to have a valid link
    url = "?" + params_.urlencode()

    return {"url": url}

@register.inclusion_tag('pyBuchaktion/list_limits.html')
def list_limits(params, current, options, default):
    return {
        "params": params,
        "options": options,
        "default": default,
        "current": current,
    }
