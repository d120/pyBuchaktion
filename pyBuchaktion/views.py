from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import UpdateView, CreateView, BaseCreateView, DeleteView
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.utils.translation import get_language
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.db.models import F, Count, ExpressionWrapper, Prefetch, ProtectedError

from .forms import BookSearchForm, ModuleSearchForm, AccountEditForm, BookOrderForm, BookProposeForm, LiteratureCreateForm
from .models import Book, Module, Order, Student, OrderTimeframe, ModuleCategory, Literature
from .mixins import SearchFormContextMixin, StudentRequestMixin, StudentRequiredMixin, NeverCacheMixin, UnregisteredStudentRequiredMixin


class VarPagedListView(ListView):

    """
        A list view specialization for making the paginate_by value
        possible to set by the user.
    """

    # The default pagination setting
    paginate_by_default = 10
    # The options for pagination
    paginate_by_options = [10, 25, 50, 100]

    # Get the paginate by value
    def get_paginate_by(self, queryset):
        opts = self.request.GET
        if 'limit' in opts:
            try:
                limit = int(opts['limit'])
                self.paginate_by = limit
            except (TypeError, ValueError):
                self.paginate_by = self.paginate_by_default
        else:
            self.paginate_by = self.paginate_by_default

        return self.paginate_by

    # Overwrite the context to add information on pagination
    # as well as the GET parameters
    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        context['get_params'] = self.request.GET
        context['limit_data'] = {
            'options': self.paginate_by_options,
            'default': self.paginate_by_default,
            'current': self.paginate_by,
        }
        return context


class BookListView(StudentRequestMixin, SearchFormContextMixin, VarPagedListView):

    """
    The list view for all the accepted books.
    """

    queryset = Book.objects.filter(state=Book.ACCEPTED)
    form_class = BookSearchForm
    template_name = 'pyBuchaktion/books/active_list.html'
    context_object_name = 'books'

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.student:
            queryset = Order.objects.student_annotate_book_queryset(self.request.student, queryset)

        return queryset


class AllBookListView(BookListView):

    """
    The list view for all books that are available.
    """

    queryset = Book.objects.all()
    template_name = 'pyBuchaktion/books/all_list.html'


class BookView(StudentRequestMixin, NeverCacheMixin, DetailView):
    """
    The detail view for a single book.
    """
    model = Book

    def get_context_data(self, **kwargs):
        context = super(BookView, self).get_context_data(**kwargs)
        if hasattr(self.request, 'student') and self.request.student is not None:
                orders = self.object.order_set.filter(student=self.request.student)
                context.update({'orders': orders})
        return context


class BookOrderView(StudentRequiredMixin, NeverCacheMixin, CreateView):
    model = Book
    form_class = BookOrderForm
    template_name_suffix = '_order_form'

    def get_success_url(self):
        return reverse("pyBuchaktion:book", kwargs=self.kwargs)

    def get_invalid_url(self):
        return self.get_success_url()

    def get_form_kwargs(self):
        kwargs = super(BookOrderView, self).get_form_kwargs()
        kwargs.update({'instance': Order(
            book = Book.objects.get(pk=self.kwargs['pk']),
            status = Order.PENDING,
            student = self.request.student,
            order_timeframe = OrderTimeframe.objects.current(),
        )})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(BookOrderView, self).get_context_data(**kwargs)
        timeframe = OrderTimeframe.objects.current();
        if timeframe:
            context.update({'current_timeframe': timeframe.end_date})
        try:
            context.update({'book' : self.model.objects.get(pk=self.kwargs['pk'])})
        except self.model.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': self.model._meta.verbose_name})
        return context


class ModuleListView(StudentRequestMixin, SearchFormContextMixin, VarPagedListView):

    """
    The list view for all modules.
    """

    model = Module
    template_name = 'pyBuchaktion/module_list.html'
    context_object_name = 'modules'
    form_class = ModuleSearchForm

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.annotate(book_count=Count('literature')).filter(book_count__gt=0)

    def get_localized_field(self, field_key):
        if field_key == 'name':
            return 'name_' + get_language()


class ModuleDetailView(StudentRequestMixin, DetailView):

    """
    The view for one specific module.
    """

    model = Module
    template_name = 'pyBuchaktion/module.html'
    context_object_name = 'module'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        books = Book.objects.filter(literature_info__module=self.object)
        books = books.filter(state=Book.ACCEPTED)
        get_args = {'literature_info__source': Literature.STUDENT}
        literature = books.exclude(**get_args)
        recommendations = books.filter(**get_args)
        if self.request.student:
            literature = Order.objects.student_annotate_book_queryset(
                self.request.student, literature,
            ).all()
            recommendations = Order.objects.student_annotate_book_queryset(
                self.request.student, recommendations,
            ).all()
        context.update({
            'literature': literature,
            'recommendations': recommendations,
        })
        return context


class ModuleCategoriesView(StudentRequestMixin, ListView):
    """
    The view that displays all modules within the respective category
    """
    model = ModuleCategory

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'misc_module_list': Module.objects.filter(category=None)})
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(visible=True)
        queryset = queryset.annotate(module_count=Count('module'))
        queryset = queryset.filter(module_count__gt=0)
        modules = Module.objects.annotate(book_count=Count('literature'))
        queryset = queryset.prefetch_related(
            Prefetch('module_set', queryset=modules)
        )
        return queryset


class OrderListView(StudentRequiredMixin, NeverCacheMixin, VarPagedListView):

    def get_queryset(self):
        return Order.objects.filter(student=self.request.student)


class OrderDetailView(StudentRequiredMixin, NeverCacheMixin, DetailView):

    def get_queryset(self):
        student = self.request.student
        return Order.objects.filter(student=student)


class OrderAbortView(DeleteView, OrderDetailView):
    template_name_suffix = '_abort'

    def delete(self, request, *args, **kwargs):
        order = self.get_object()
        if order.status == Order.PENDING:
            return super(OrderAbortView, self).delete(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse("pyBuchaktion:order", kwargs=kwargs))

    def get_success_url(self):
        return reverse("pyBuchaktion:account")


class AccountView(StudentRequiredMixin, NeverCacheMixin, UpdateView):
    template_name = 'pyBuchaktion/account.html'

    def get_form_class(self):
        return AccountEditForm

    def get_success_url(self):
        return reverse("pyBuchaktion:account")

    def get_object(self, queryset=None):
        return self.request.student

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        timeframe = OrderTimeframe.objects.current()
        if timeframe:
            context_name = 'timeframe'
        else:
            timeframe = OrderTimeframe.objects.upcoming()
            if timeframe:
                context_name = 'timeframe_upcoming'

        if timeframe:
            budget_spent = Order.objects.student_semester_order_count(self.request.student, timeframe.semester)
            budget_max = OrderTimeframe.objects.semester_budget(timeframe.semester)

            context.update({
                context_name: timeframe,
                'budget': {
                    'spent': budget_spent,
                    'max': budget_max,
                    'left': budget_max - budget_spent,
                },
            })

        return context


class AccountCreateView(UnregisteredStudentRequiredMixin, NeverCacheMixin, CreateView):
    template_name = 'pyBuchaktion/account_create.html'

    def get_form_class(self):
        return AccountEditForm

    def get_success_url(self):
        return reverse("pyBuchaktion:account")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if kwargs['instance'] is None:
            kwargs['instance'] = Student()
            tuid_user = self.request.TUIDUser
            kwargs['instance'].tuid_user = tuid_user
            lang = get_language()
            if lang in (key for key, name in Student.LANG_CHOICES):
                kwargs['instance'].language = lang
            kwargs['initial'] = {'email': tuid_user.email}
        return kwargs

class AccountDeleteView(StudentRequiredMixin, NeverCacheMixin, TemplateView):
    template_name = 'pyBuchaktion/account_delete.html'

    def post(self, request):
        try:
            request.TUIDUser.delete()
        except ProtectedError as e:
            return render(request, self.template_name, {'error': e})
        return HttpResponseRedirect(reverse('pyBuchaktion:books'))

class BookProposeView(StudentRequiredMixin, CreateView):
    model = Book
    template_name_suffix = '_propose'
    form_class = BookProposeForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.student = self.request.student
        return form

    def form_valid(self, form):
        form.instance.state = Book.PROPOSED
        result = super().form_valid(form)
        order = Order(
            book=form.instance,
            student=self.request.student,
            status=Order.PENDING,
            order_timeframe=OrderTimeframe.objects.current()
        )
        order.save()
        return result

    def form_invalid(self, form):
        if form.has_error('isbn_13', 'unique'):
            try:
                book = Book.objects.get(isbn_13=self.request.POST.get('isbn_13', None))
                return HttpResponseRedirect(reverse('pyBuchaktion:book', kwargs={'pk': book.pk}))
            except (TypeError, ValueError, Book.DoesNotExist) as e:
                form.add_error(ValidationError(e))
        return super().form_invalid(form)


class LiteratureCreateView(StudentRequiredMixin, CreateView):
    model = Module
    form_class = LiteratureCreateForm
    template_name_suffix = '_literature_create'

    def get_success_url(self):
        return reverse("pyBuchaktion:module", kwargs={'pk': self.object.module.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if kwargs['instance'] is None:
            kwargs['instance'] = Literature()
            kwargs['instance'].module = Module.objects.get(pk=self.kwargs.get('pk', None))
            kwargs['instance'].source = Literature.STUDENT
            kwargs['instance'].in_tucan = False
            kwargs['instance'].active = True
        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # form.fields["book"].queryset = Book.objects.filter(state=Book.ACCEPTED)
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'module': Module.objects.get(pk=self.kwargs.get('pk', None))})
        return context
