from datetime import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.http.request import QueryDict
from django.db.models import Sum

from .models import Student, Order, Book, OrderTimeframe

class BookOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = []

    def clean(self):
        order = self.instance
        student = order.student
        book = order.book

        # Can the book be ordered
        if book.state not in (Book.ACCEPTED, Book.PROPOSED):
            raise ValidationError(_("This book is not available for ordering"), code='not_available')

        # does the student have an order for this already
        # if Order.objects.student_book_order_count(student, book) > 0:
        #    raise ValidationError(_("You already ordered this book"), code='already_ordered')

        timeframe = OrderTimeframe.objects.current()
        if not timeframe:
            raise ValidationError(_("Book ordering is not active for the current date"), code='no_timeframe')

        semester = timeframe.semester
        budget_spent = Order.objects.student_semester_order_count(student, semester)
        budget_max = OrderTimeframe.objects.semester_budget(semester)
        budget_left = budget_max - budget_spent

        if budget_left <= 0:
            raise ValidationError(_("You may not order any more books in this timeframe."), code='no_budget_left')



class BookSearchForm(forms.Form):
    title = forms.CharField(label=_("Title"), max_length=100, required=False)
    author = forms.CharField(label=_("Author"), max_length=100, required=False)
    isbn_13 = forms.CharField(label=_("ISBN-13"), max_length=13, required=False)
    publisher = forms.CharField(label=_("Publisher"), max_length=64, required=False)


class BookProposeForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['isbn_13', 'title', 'author', 'publisher', 'year']

    def clean(self):
        cleaned_data = super().clean()
        book = self.instance
        student = self.student

        timeframe = OrderTimeframe.objects.current()
        if not timeframe:
            raise ValidationError(_("Book proposal is not active for the current date."), code='no_timeframe')

        semester = timeframe.semester
        budget_spent = Order.objects.student_semester_order_count(student, semester)
        budget_max = OrderTimeframe.objects.semester_budget(semester)
        budget_left = budget_max - budget_spent

        if budget_left <= 0:
            raise ValidationError(_("You may not order or propose any more books in this timeframe."), code='no_budget_left')

        return cleaned_data


class ModuleSearchForm(forms.Form):
    name = forms.CharField(label=_("Name"), max_length=100, required=False)
    module_id = forms.CharField(label="Module ID", max_length=13, required=False)


class AccountEditForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['email', 'library_id', 'language']
        help_texts = {
            'library_id': _("The library id number assigned by the ULB, required for if you want the book to be reserved for you"),
            'language': _("The preferred language for notification emails"),
            'email': _("The e-mail address to recieve status updates"),
        }
