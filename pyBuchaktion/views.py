from django.views.generic import ListView, DetailView, TemplateView, View
from django.views.generic.base import ContextMixin
from django.views.generic.list import MultipleObjectMixin
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import UpdateView, CreateView
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.core.serializers.python import Serializer
from django.http import HttpResponseRedirect, HttpResponse
from .data import get_logged_in_student, post_order_book, post_abort_order, _model_to_dict, current_timeframe
from .forms import BookSearchForm, ModuleSearchForm, AccountEditForm, BookOrderForm
from .models import Book, TucanModule, Order, Student


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

class FormContextMixin(ContextMixin):

    """
        A mixin to add the form provided to the context
    """

    # The form for this mixin
    form = None

    def get_form(self):
        return self.form

    def get_context_data(self, **kwargs):
        context = super(FormContextMixin, self).get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context

class StudentContextMixin(ContextMixin):
    """
    A mixin the provides the currently logged in student to the context.
    """
    def get_context_data(self, **kwargs):
        context = super(StudentContextMixin, self).get_context_data(**kwargs)
        context['student'] = get_logged_in_student(self.request)
        return context

class BookListView(FormContextMixin, VarPagedListView):

    """
        The list view for all the accepted books.
    """

    queryset = Book.objects.filter(state=Book.ACCEPTED)
    template_name = 'pyBuchaktion/books/active_list.html'
    context_object_name = 'books'

    def get_queryset(self):
        self.form = BookSearchForm(self.request.GET)
        queryset = super(BookListView, self).get_queryset()

        if self.form.is_valid():
            data = self.form.cleaned_data

            author_search = data['author']
            queryset = queryset.filter(author__contains=author_search)

            title_search = data['title']
            queryset = queryset.filter(title__contains=title_search)

            isbn_search = data['isbn_13']
            if (isbn_search != ""):
                queryset = queryset.filter(isbn_13=isbn_search)

        return queryset

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


class BookView(StudentContextMixin, DetailView):
    """
    The detail view for a single book.
    """
    model = Book

    def get_context_data(self, **kwargs):
        context = super(BookView, self).get_context_data(**kwargs)
        if context['student'] and context['book']:
            context['orders'] = context['book'].order_set.filter(student=context['student'])
        return context

class BookOrderView(CreateView, BookView):
    model = Book
    form_class = BookOrderForm
    template_name_suffix = '_order_form'

    def get_success_url(self):
        return reverse("pyBuchaktion:book", kwargs=self.kwargs)

    def form_valid(self, form):
        form.instance.book = Book.objects.get(pk=self.kwargs['pk'])
        form.instance.status = Order.PENDING
        form.instance.student = get_logged_in_student(self.request)
        form.instance.order_timeframe = current_timeframe()
        return super(BookOrderView, self).form_valid(form)

class ModuleListView(VarPagedListView, FormContextMixin):

    """ The list view for all TUCaN modules """

    template_name = 'pyBuchaktion/modules.html'
    context_object_name = 'modules'

    def get_queryset(self):
        self.form = ModuleSearchForm(self.request.GET)
        queryset = TucanModule.objects.all()

        if (self.form.is_valid()):
            data = self.form.cleaned_data

            queryset = queryset.filter(name__contains=data['name'])

            if (data['module_id'] != ""):
                queryset = queryset.filter(module_id=data['module_id'])

        return queryset

class ModuleDetailView(DetailView):
    template_name = 'pyBuchaktion/module.html'
    context_object_name = 'module'
    model = TucanModule

class OrderListView(VarPagedListView):

    def get_queryset(self):
        return Order.objects.filter(student=get_logged_in_student(self.request))

class OrderDetailView(DetailView):

    def get_queryset(self):
        student = get_logged_in_student(self.request)
        return Order.objects.filter(student=student)

    def post(self, request, *args, **kwargs):
        if 'action' in request.POST and request.POST['action'] == "Abort":
            _id = kwargs.get('pk')
            if _id:
                try:
                    order = self.get_queryset().get(pk=_id)
                    if order.status == Order.PENDING:
                        return HttpResponseRedirect(reverse("pyBuchaktion:order_abort", kwargs=kwargs))
                except Order.DoesNotExist as e:
                    pass
        return HttpResponseRedirect(reverse("pyBuchaktion:order", kwargs=kwargs))

class OrderAbortView(OrderDetailView):
    template_name = 'pyBuchaktion/order_abort.html'

    def post(self, request, *args, **kwargs):
        if 'action' in request.POST:
            action = request.POST['action']
            if (action == "Abort"):
                self.order_abort = post_abort_order(
                    request, kwargs['pk'])
                if (self.order_abort):
                    return HttpResponseRedirect(reverse("pyBuchaktion:account"))
            elif (action == "Cancel"):
                return HttpResponseRedirect(reverse("pyBuchaktion:order", kwargs=kwargs))
        else:
            return HttpResponseRedirect(reverse("pyBuchaktion:order", kwargs=kwargs))

class AccountView(UpdateView):
    template_name = 'pyBuchaktion/account.html'

    def get_form_class(self):
        return AccountEditForm

    def get_success_url(self):
        return reverse("pyBuchaktion:account")

    def get_object(self, queryset=None):
        return get_logged_in_student(self.request)
