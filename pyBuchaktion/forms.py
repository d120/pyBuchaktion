from django import forms
from django.utils.translation import ugettext_lazy as _
from django.http.request import QueryDict

class OrderForm(forms.Form):
    pass

class BookSearchForm(forms.Form):
    title = forms.CharField(label=_("Title"), max_length=100, required=False)
    author = forms.CharField(label=_("Author"), max_length=100, required=False)
    isbn = forms.CharField(label="ISBN-13", max_length=13, required=False)
    #module = forms.CharField(label=_("Module"), max_length=100, required=False)

    def to_dict(self):
        dct = QueryDict(mutable=True);
        for field in self:
            dct[field.name] = field.value()
        return dct

class ModuleSearchForm(forms.Form):
    name = forms.CharField(label=_("Name"), max_length=100, required=False)
    module_id = forms.CharField(label="Module ID", max_length=13, required=False)

    def is_valid(self):
        return super(ModuleSearchForm, self).is_valid()
