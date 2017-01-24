from .models import Student, Book, Order, OrderTimeframe
from django.utils.translation import ugettext_lazy as _

def get_logged_in_student(request):
    #return None
	return Student.objects.get(pk=1)

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
        status = 'PD',
        hint = "-",
        book = book,
        student = student,
        # FIXME: dynamic timeframe choice
        order_timeframe = OrderTimeframe.objects.get(pk=1),
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
