from django.utils.translation import ugettext_lazy as _

from .settings import BUCHAKTION_MESSAGES_DEBUG
from .models import DisplayMessage

MESSAGES = {
    'modulecategories_list_intro':  _("This list contains all modules for which books are available for ordering through this system."),
    'book_order_active':            _("If you order now, the order will be posted to our merchant by <b>{date}</b>."),
    'book_order_inactive':          _("Book ordering is not active for the current date"),
    'book_order_intro':             "",
    'book_propose_intro':           _("You may use this form to propose a book to us. This will automatically generate an order for that book, helping us keep track on how many people would like to see the book available.\n\nYou may cancel this order at any time."),
    'proposal_order_intro':         _("This order is associated with a proposed book. Until the book is confirmed, it will not be proceeded with. In any case, this order expresses your interest in this book, which improves the chance that it will get confirmed."),
    'order_marked_date':            _("This order is marked to be ordered from our book retailer on <b>{date}<b/>."),
    'account_orders_active':        _("Below, you find the list of your orders. The current order timeframe is from <b>{start_date}</b> to <b>{end_date}</b>. You currently have <b>{budget_spent} of {budget_max}</b> available orders posted."),
    'orders_none_found':            _("No orders found!"),
    'account_no_orders':            _("You have not ordered any books!"),
    'module_not_much_literature':   _("It seems that this module does not have much literature associated with it."),
    'book_state_RJ':                _("This book has been rejected, and may not be ordered"),
    'book_state_PP':                _("This book has been proposed, but has yet to be confirmed by our team."),
    'book_state_OL':                _("This book has been marked obsolete, a new version is available. It may not be ordered"),
    'book_not_ordered':             _("You have not ordered this book"),
    'order_proposed_book':          _("Orders for proposed books will be proceeded with once the book is confirmed."),
    'account_orders_inactive':      _("At the moment, no orders may be posted!"),
    'library_id_help':              _("Your library ID number"),
    'book_not_found':               _('The book you are searching for may already have been proposed, rejected or marked as obsolete. Check the <a href="{full_list}">full list</a> to see if any of these apply, otherwise you may <a href="{propose}">propose</a> the book to us.'),
    'book_not_found_all':           _('You may propose the book to us <a href="{propose}">here</a>, or contact us via E-Mail at <a href="mailto:{email}">{email}</a>')
}

def get_message(key):

    """
    Gets the message for the associated key from the most
    customized source possible. Check the database first, then fall
    back to the MESSAGES dictionary.
    """

    if not key:
        # TODO: is this needed somewhere or can we replace this with an error?
        return ""
        # raise RuntimeException('Empty message key not allowed')

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
        return '[msg:' + key + ']'
    else:
        return ""


class Message(object):
    """
    A message object that can be used instead of get_message
    in places where the function would only be called at compile
    time, such as Meta classes. This way we don't have to restart
    the server for text changes to have an effect.

    Just use `Message('key')` instead of `get_message('key')`.
    """

    # Creates a new message object
    def __init__(self, key):

        if not key:
            raise RuntimeException('Empty message key not allowed')
        self.key = key

    # Gets the represented message
    def __repr__(self):
        return get_message(self.key)
