from datetime import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.http.request import QueryDict
from django.db.models import Sum

from .messages import get_message, Message
from . import models

import isbnlib



class BookOrderForm(forms.ModelForm):
    """
    Form used to order a single book. Requires to be created with an instance
    of Order containing book and student to perform correct validation.
    """

    class Meta:
        model = models.Order
        fields = []

    def clean(self):
        order = self.instance
        student = order.student
        book = order.book

        # Can the book be ordered
        if book.state not in (models.Book.ACCEPTED, models.Book.PROPOSED):
            raise ValidationError(_("This book is not available for ordering"), code='not_available')

        # does the student have an order for this already
        # if Order.objects.student_book_order_count(student, book) > 0:
        #    raise ValidationError(_("You already ordered this book"), code='already_ordered')

        timeframe = models.OrderTimeframe.objects.current()
        if not timeframe:
            raise ValidationError(_("Book ordering is not active for the current date"), code='no_timeframe')

        semester = timeframe.semester
        budget_spent = models.Order.objects.student_semester_order_count(student, semester)
        budget_max = models.OrderTimeframe.objects.semester_budget(semester)
        budget_left = budget_max - budget_spent

        if budget_left <= 0:
            raise ValidationError(_("You may not order any more books in this timeframe."), code='no_budget_left')


class LiteratureCreateForm(forms.ModelForm):
    """
    Form to create a literatur model, which is the bridge between a book and a module.
    """

    class Meta:
        model = models.Literature
        fields = ['book']

    def clean(self):
        cleaned_data = super().clean()
        literature = self.instance

        book = cleaned_data['book']

        # if book.state != Book.ACCEPTED:
        #    raise ValidationError({'book':_("This book has not been accepted yet")}, code='not_accepted')

        if models.Literature.objects.filter(module=literature.module, book=book).count() > 0:
            raise ValidationError({'book':_("This book is already proposed for this module")}, code='exists')

        return cleaned_data


class BookSearchForm(forms.Form):
    title = forms.CharField(label=_("Title"), max_length=100, required=False)
    author = forms.CharField(label=_("Author"), max_length=100, required=False)
    isbn_13 = forms.CharField(label=_("ISBN-13"), max_length=13, required=False)
    publisher = forms.CharField(label=_("Publisher"), max_length=64, required=False)


class BookProposeForm(forms.ModelForm):

    # Custom isbn_13 field to allow XXX-XX-XXXXX-XX-X format
    isbn_13 = forms.CharField(label=_("ISBN-13"), max_length=17, required=True)

    class Meta:
        model = models.Book
        fields = ['isbn_13', 'title', 'author', 'publisher', 'year']

    def clean(self):
        cleaned_data = super().clean()
        student = self.student

        # Remove all non digit characters from the ISBN
        cleaned_data['isbn_13'] = isbnlib.canonical(cleaned_data['isbn_13'])

        if not isbnlib.is_isbn13(cleaned_data['isbn_13']):
            raise ValidationError({'isbn_13': _("Not a valid ISBN-13")}, code='isbn_invalid')

        # Get the current timeframe
        timeframe = models.OrderTimeframe.objects.current()
        if not timeframe:
            raise ValidationError(_("Book proposal is not active for the current date."), code='no_timeframe')

        semester = timeframe.semester
        budget_spent = models.Order.objects.student_semester_order_count(student, semester)
        budget_max = models.OrderTimeframe.objects.semester_budget(semester)
        budget_left = budget_max - budget_spent

        if budget_left <= 0:
            raise ValidationError(_("You may not order or propose any more books in this timeframe."), code='no_budget_left')

        return cleaned_data


class ModuleSearchForm(forms.Form):
    name = forms.CharField(label=_("Name"), max_length=100, required=False)
    module_id = forms.CharField(label="Module ID", max_length=13, required=False)


class AccountEditForm(forms.ModelForm):

    class Meta:
        model = models.Student
        fields = ['email', 'library_id', 'language']
        help_texts = {
            'library_id': Message('library_id_help'),
            'language': _("The preferred language for notification emails"),
            'email': _("The e-mail address to recieve status updates"),
        }

class OrderTimeframeForm(forms.ModelForm):

    def clean(self):
        if self.cleaned_data['start_date'] > self.cleaned_data['end_date']:
            raise ValidationError(_("start date must be before end date"))
        return self.cleaned_data

    class Meta:
        model = models.OrderTimeframe
        fields = ['semester', 'start_date', 'end_date', 'allowed_orders', 'spendings']
