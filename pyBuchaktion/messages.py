from django.utils.translation import ugettext_lazy as _

from .settings import BUCHAKTION_MESSAGES_DEBUG
from .models import DisplayMessage

MESSAGES = {
    'modulecategories_list_intro': _("This list contains all modules for which books are available for ordering through this system."),
    'book_order_active': _("If you order now, the order will be posted to our merchant by <b>{date}</b>."),
    'book_order_inactive': _("Book ordering is not active for the current date"),
    'book_order_intro': "",
    'book_propose_intro': _("You may use this form to propose a book to us. This "
        "will automatically generate an order for that book for the current timeframe, "
        "helping us keep track on how many people would like to see the book available. \n\n"
        "You may cancel this order at any time, revoking your contribution to proposing this book."),
    'proposal_order_intro': _("This order is associated with a proposed book. "
        "Until the book is confirmed, it will not be proceeded with. In any case, this order "
        "expresses your interest in this book, which improves the chance that it will get confirmed."),
    'order_marked_date': _("This order is marked to be ordered from our book retailer on <b>{date}<b/>."),
    'account_orders_active': _("Below, you find the list of your orders. The current order timeframe is "
        "from <b>{start_date}</b> to <b>{end_date}</b>. You currently have <b>{budget_spent} "
        "of {budget_max}</b> available orders posted."),
    'orders_none_found': _("No orders found!"),
    'account_no_orders': _("You have not ordered any books!"),
    'module_no_literature': _("It seems that this module does not have any literature associated with it.")
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
