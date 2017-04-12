from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.http.request import QueryDict
from .models import Student, Order, Book

class BookOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = []

    def clean(self):
        # Can the book be ordered
        if self.instance.book.state != Book.ACCEPTED:
            raise ValidationError(_("This book is not available for ordering"), code='not_available')

        # does the student have an order for this already
        if self.instance.student.order_set.filter(book__pk=self.instance.book_id).count() > 0:
            raise ValidationError(_("You already ordered this book"), code='already_ordered')

class BookSearchForm(forms.Form):
    title = forms.CharField(label=_("Title"), max_length=100, required=False)
    author = forms.CharField(label=_("Author"), max_length=100, required=False)
    isbn_13 = forms.CharField(label=_("ISBN-13"), max_length=13, required=False)
    publisher = forms.CharField(label=_("Publisher"), max_length=64, required=False)

class ModuleSearchForm(forms.Form):
    name = forms.CharField(label=_("Name"), max_length=100, required=False)
    module_id = forms.CharField(label="Module ID", max_length=13, required=False)

    def is_valid(self):
        return super(ModuleSearchForm, self).is_valid()


class AccountEditForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['library_id']
        help_texts = {'library_id': _("The library id number assigned by the ULB")}
