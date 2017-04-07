from django import forms
from django.utils.translation import ugettext_lazy as _
from django.http.request import QueryDict
from .models import Student

class OrderForm(forms.Form):
    pass

class BookSearchForm(forms.Form):
    title = forms.CharField(label=_("Title"), max_length=100, required=False)
    author = forms.CharField(label=_("Author"), max_length=100, required=False)
    isbn_13 = forms.CharField(label="ISBN-13", max_length=13, required=False)

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
