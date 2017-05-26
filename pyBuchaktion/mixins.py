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

def get_student_from_tuid(tuid_user):
    if not tuid_user:
        return None
    return Student.objects.filter(tuid_user=tuid_user).first()


class TUIDUserContextMixin(ContextMixin):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'tuid_user': self.request.TUIDUser})
        return context


class BuchaktionGroupLoginRequiredMixin(TUIDUserContextMixin, TUIDUserInGroupMixin):

    group_required = BUCHAKTION_STUDENT_LDAP_GROUP
    permission_denied_message = _("This function is only available for students from faculty 20!")


class StudentContextMixin(ContextMixin):

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        if (hasattr(self, 'student')):
            context.update({'student': self.student})
        return context


class StudentRequestMixin(StudentContextMixin, View):

    def dispatch(self, request, *args, **kwargs):
        self.student = get_student_from_tuid(self.request.TUIDUser)
        return super().dispatch(request, *args, **kwargs)


class StudentRequiredMixin(StudentContextMixin, View):

    def get_unregistered_redirect(self):
        return reverse('pyBuchaktion:account_create')

    def dispatch(self, request, *args, **kwargs):
        student = get_student_from_tuid(self.request.TUIDUser)
        if student:
            self.student = student
            return super().dispatch(request, *args, **kwargs)
        return HttpResponseRedirect(self.get_unregistered_redirect())


class StudentLoginRequiredMixin(BuchaktionGroupLoginRequiredMixin, StudentRequiredMixin):
    pass


class UnregisteredUserRequiredMixin(View):

    def get_registered_redirect(self):
        return reverse('pyBuchaktion:account')

    def dispatch(self, request, *args, **kwargs):
        student = get_student_from_tuid(request.TUIDUser)
        if student:
            return HttpResponseRedirect(self.get_registered_redirect())
        return super().dispatch(request, *args, **kwargs)


class UnregisteredStudentLoginRequiredMixin(BuchaktionGroupLoginRequiredMixin, UnregisteredUserRequiredMixin):
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

    def get_form_queryset(self, data, queryset):
        for key, value in data.items():
            for val in value.split():
                kwargs = {key + "__icontains": val}
                queryset = queryset.filter(**kwargs)
        return queryset

    def get_queryset(self):
        queryset = super(SearchFormContextMixin, self).get_queryset()
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
