from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.views.generic import View
from django.views.generic.base import ContextMixin
from django.utils.cache import add_never_cache_headers
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect

from pyTUID.mixins import TUIDLoginRequiredMixin, TUIDUserInGroupMixin

from .models import Student
from .settings import BUCHAKTION_STUDENT_LDAP_GROUP


class LDAPLoginGate(TUIDUserInGroupMixin):

    group_required = BUCHAKTION_STUDENT_LDAP_GROUP
    permission_denied_message = _("This feature is only available for students at the department of computer science! (dept. 20)")


class StudentRequestMixin(View):

    def dispatch(self, request, *args, **kwargs):
        request.student = Student.objects.from_tuid(request.TUIDUser)
        return super().dispatch(request, *args, **kwargs)


class StudentGate(View):

    def get_unregistered_redirect(self):
        return reverse('pyBuchaktion:account_create')

    def dispatch_unregistered(self, request, *args, **kwargs):
        return HttpResponseRedirect(self.get_unregistered_redirect())

    def dispatch(self, request, *args, **kwargs):
        if request.student:
            return super().dispatch(request, *args, **kwargs)
        else:
            return self.dispatch_unregistered(request, *args, **kwargs)


class NoStudentGate(View):

    def get_registered_redirect(self):
        return reverse('pyBuchaktion:account')

    def dispatch_registered(self, request, *args, **kwargs):
        return HttpResponseRedirect(self.get_registered_redirect())

    def dispatch(self, request, *args, **kwargs):
        if request.student:
            return self.dispatch_registered(request, *args, **kwargs)
        else:
            return super().dispatch(request, *args, **kwargs)


class StudentRequiredMixin(LDAPLoginGate, StudentRequestMixin, StudentGate):
    pass

class UnregisteredStudentRequiredMixin(LDAPLoginGate, StudentRequestMixin, NoStudentGate):
    pass


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

    def get_localized_field(self, field_key):
        return field_key

    def get_form_queryset(self, data, queryset):
        for key, value in data.items():
            key = self.get_localized_field(key)
            for val in value.split():
                kwargs = {key + "__icontains": val}
                queryset = queryset.filter(**kwargs)
        return queryset

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.form.is_valid():
            queryset = self.get_form_queryset(self.request.form.cleaned_data, queryset)
        return queryset


class ForeignKeyImportResourceMixin(object):

    def init_instance(self, row=None):
        """
        Initializes a new Django model.
        """
        instance = self._meta.model()
        if row:
            for key, value in row.items():
                target = key.split("__", 1)
                field_name = target[0]
                if len(target) > 1:
                    target_query = target[1]
                    foreign_model = self._meta.model._meta.get_field(field_name).rel.to
                    args = {target_query: row[key]}
                    setattr(instance, field_name, foreign_model.objects.get(**args))

        return instance


class NeverCacheMixin(View):

    def dispatch(self, request, *args, **kwargs):
        response = super(NeverCacheMixin, self).dispatch(request, *args, **kwargs)
        add_never_cache_headers(response)
        return response
