from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, CreateView, BaseCreateView, DeleteView
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from .forms import BookSearchForm, ModuleSearchForm, AccountEditForm, BookOrderForm, BookProposeForm
from .models import Book, TucanModule, Order, Student, OrderTimeframe
from .mixins import SearchFormContextMixin, StudentContextMixin, StudentLoginRequiredMixin, NeverCacheMixin


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
            limit = int(opts['limit'])
            if (limit in self.paginate_by_options):
                self.paginate_by = limit
        else:
            self.paginate_by = self.paginate_by_default

        return self.paginate_by

    # Overwrite the context to add information on pagination
    # as well as the GET parameters
    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        context['get_params'] = self.request.GET
        context['limit'] = self.paginate_by
        context['limit_options'] = self.paginate_by_options
        context['limit_default'] = self.paginate_by_default
        return context


class BookListView(StudentContextMixin, SearchFormContextMixin, VarPagedListView):

    """
    The list view for all the accepted books.
    """

    queryset = Book.objects.filter(state=Book.ACCEPTED)
    form_class = BookSearchForm
    template_name = 'pyBuchaktion/books/active_list.html'
    context_object_name = 'books'


class AllBookListView(BookListView):

    """
    The list view for all books that are available.
    """

    queryset = Book.objects.all()
    template_name = 'pyBuchaktion/books/all_list.html'

    def get_context_data(self, **kwargs):
        context = super(AllBookListView, self).get_context_data(**kwargs)
        context['showtag'] = True
        return context


class BookView(StudentContextMixin, NeverCacheMixin, DetailView):
    """
    The detail view for a single book.
    """
    model = Book

    def get_context_data(self, **kwargs):
        context = super(BookView, self).get_context_data(**kwargs)
        if 'student' in context and 'book' in context:
            if context['student'] and context['book']:
                context['orders'] = context['book'].order_set.filter(student=context['student'])
        return context


class BookOrderView(StudentLoginRequiredMixin, NeverCacheMixin, CreateView):
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
            order_timeframe = OrderTimeframe.current(),
        )})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(BookOrderView, self).get_context_data(**kwargs)
        context.update({'student': self.request.student})
        try:
            context.update({'book' : self.model.objects.get(pk=self.kwargs['pk'])})
        except self.model.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': self.model._meta.verbose_name})
        return context


class ModuleListView(StudentContextMixin, SearchFormContextMixin, VarPagedListView):

    """
    The list view for all TUCaN modules.
    """

    model = TucanModule
    template_name = 'pyBuchaktion/module_list.html'
    context_object_name = 'modules'
    form_class = ModuleSearchForm


class ModuleDetailView(StudentContextMixin, DetailView):

    """
    The view for one specific module.
    """

    model = TucanModule
    template_name = 'pyBuchaktion/module.html'
    context_object_name = 'module'


class OrderListView(StudentLoginRequiredMixin, NeverCacheMixin, VarPagedListView):

    def get_queryset(self):
        return Order.objects.filter(student=self.request.student)


class OrderDetailView(StudentLoginRequiredMixin, NeverCacheMixin, DetailView):

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


class AccountView(StudentLoginRequiredMixin, NeverCacheMixin, UpdateView):
    template_name = 'pyBuchaktion/account.html'

    def get_form_class(self):
        return AccountEditForm

    def get_success_url(self):
        return reverse("pyBuchaktion:account")

    def get_object(self, queryset=None):
        return self.request.student


class BookProposeView(StudentLoginRequiredMixin, CreateView):
    template_name_suffix = '_propose'

    form_class = BookProposeForm

    def get_initial(self):
        return {'state': Book.PROPOSED, 'price': 0}

    def form_valid(self, form):
        order = Order(
            book=form.instance,
            student=self.request.student,
            status=Order.PENDING,
            order_timeframe=OrderTimeframe.current()
        )
        order.save()
        return super(BookProposeView, self).form_valid(form)
