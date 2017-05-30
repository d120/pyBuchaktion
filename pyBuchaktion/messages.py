from django.utils.translation import ugettext_lazy as _

from .settings import BUCHAKTION_MESSAGES_DEBUG
from .models import DisplayMessage

MESSAGES = {
    'modulecategories_list_intro': _("This list contains all modules for which books are available for ordering through this system."),
    'book_order_active': _("If you order now, the order will be posted to our merchant by <b>{date}</b>."),
    'book_order_inactive': _("Book ordering is not active for the current date"),
    'book_order_intro': "",
}

def get_message(key):
    if not key:
        return ""

    # Try the display message objects
    display_message = DisplayMessage.objects.filter(key=key).first()
    if display_message:
        return display_message.text()

    # Try the messages list
    message = MESSAGES.get(key)
    if message:
        return message

    # When nothing was found, check for debug flag
    if BUCHAKTION_MESSAGES_DEBUG and message == None:
        return '\\' + key + '\\'
    else:
        return ""
