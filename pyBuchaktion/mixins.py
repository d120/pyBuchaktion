from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.views.generic import View
from django.views.generic.base import ContextMixin
from django.http import HttpResponseRedirect

from pyTUID.mixins import TUIDLoginRequiredMixin

from .models import Student

class SearchFormContextMixin(ContextMixin):

    """
        A mixin to add the form provided to the context
    """

    form_class = None

    def get_form_class(self):
        return self.form_class

    def get(self, request, *args, **kwargs):
        fc = self.get_form_class()
        if not fc:
            raise ImproperlyConfigured(
                '{0} is missing the form_class attribute. Define '
                '{0}.form_class.'.format(self.__class__.__name__)
            )
        request.form = fc(request.GET)
        return super(SearchFormContextMixin, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SearchFormContextMixin, self).get_context_data(**kwargs)
        context['form'] = self.request.form
        return context

    def get_form_queryset(self, data, queryset):
        for key, value in data.items():
            kwargs = {key + "__contains": value}
            queryset = queryset.filter(**kwargs)

        return queryset

    def get_queryset(self):
        queryset = super(SearchFormContextMixin, self).get_queryset()
        if self.request.form.is_valid():
            queryset = self.get_form_queryset(self.request.form.cleaned_data, queryset)
        return queryset


class StudentContextMixin(object):
    """
    A mixin the provides the currently logged in student to the context.
    """
    def dispatch(self, request, *args, **kwargs):
        if request.TUIDUser:
            student = Student.from_tuid(request.TUIDUser)
            if student:
                self.request.student = student

        return super(StudentContextMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(StudentContextMixin, self).get_context_data(**kwargs)
        if self.request.student:
            context['student'] = self.request.student

        return context

class BaseStudentLoginRequiredMixin(View):

    invalid_url = None

    def get_invalid_url(self):
        return self.invalid_url

    def dispatch(self, request, *args, **kwargs):
        url = self.get_invalid_url()
        if not url:
            raise ImproperlyConfigured(
                '{0} is missing the invalid_url attribute. Define '
                '{0}.invalid_url.'.format(self.__class__.__name__)
            )

        if self.request.student:
            return super(BaseStudentLoginRequiredMixin, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(url)

class StudentLoginRequiredMixin(TUIDLoginRequiredMixin, StudentContextMixin, BaseStudentLoginRequiredMixin):

    def get_invalid_url(self):
        return reverse("pyBuchaktion:books")
