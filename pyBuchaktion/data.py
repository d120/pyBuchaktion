from django.utils.translation import ugettext_lazy as _

from .models import Student, Book, Order, OrderTimeframe

def get_logged_in_student(request):
    """
    Get the student that is currently logged in.
    """

    return None

def post_order_book(request, book_id):
    # is user logged in
    student = get_logged_in_student(request)
    if (student == None):
        return _("You are not logged in!")

    # does the book id exist
    try:
        book = Book.objects.get(pk=book_id)
    except Book.DoesNotExist:
        return _("This book does not exist")

    # does the student have an order for this already
    try:
        book_order = student.order_set.get(book__pk=book_id)
        return _("You already ordered this book")
    except Order.DoesNotExist:
        pass

    # is the book avaliable for ordering (accepted) 
    if (book.state != 'AC'):
        return _("This book is not available for ordering")
    
    # FIXME: check order balance (and adjust)

    # else create the order entry
    order = Order.objects.create(
        status = Order.PENDING,
        book = book,
        student = student,
        order_timeframe = current_timeframe()
    )
    return True

def post_abort_order(request, order_id):
    student = get_logged_in_student(request)
    if (student == None):
        return _("Not logged in")

    try:
        order = student.order_set.get(pk=order_id)
    except Order.DoesNotExist:
        return _("Order not found")

    order.delete()
    return True

def _model_to_dict(instance, fields=None, exclude=None):
    """
    Returns a dict containing the data in ``instance`` along with any foreign
    keys returned as their respective natural key, if available.

    ``fields`` is an optional list of field names. If provided, only the named
    fields will be included in the returned dict.

    ``exclude`` is an optional list of field names. If provided, the named
    fields will be excluded from the returned dict, even if they are listed in
    the ``fields`` argument.
    """
    opts = instance._meta
    data = {}
    for f in opts.get_fields():
        if not getattr(f, 'editable', False):
            continue
        if fields and f.name not in fields:
            continue
        if exclude and f.name in exclude:
            continue
        val = f.value_from_object(instance)

        if (isinstance(val, QuerySet)):
            data[f.name] = [i.natural_key() for i in val]
            continue
        if (isinstance(f, ForeignKey)):
            obj = f.rel.to.objects.get(pk=val)
            if (hasattr(obj, 'natural_key')):
                data[f.name] = obj.natural_key()
            else:
                data[f.name] = val
            continue
        data[f.name] = val
    return data
