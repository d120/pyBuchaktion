from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import ProcessFormView, FormMixin
from .models import Book, TucanModule, Student, Order
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from .data import get_logged_in_student, post_order_book, post_abort_order
from .forms import OrderForm, BookSearchForm, ModuleSearchForm

class VarPagedListView(ListView):
    paginate_by_default = 10
    paginate_by_sizes = [10, 25, 50, 100]

    def get_paginate_by(self, queryset):
        try:
            size = int(self.request.GET['size'])
            if (size in self.paginate_by_sizes):
                self.paginate_by = size
        except:
            self.paginate_by = self.paginate_by_default
            pass

        return self.paginate_by

    def get_context_data(self, **kwargs):
        context = super(VarPagedListView, self).get_context_data(**kwargs)
        context['get_params'] = self.request.GET
        context['size'] = self.paginate_by
        context['sizes'] = self.paginate_by_sizes
        context['size_default'] = self.paginate_by_default
        return context

class BookListView(VarPagedListView):
    queryset = Book.objects.filter(state=Book.ACCEPTED)
    template_name = 'pyBuchaktion/books.html'
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

            isbn_search = data['isbn']
            if (isbn_search != ""):
                queryset = queryset.filter(isbn_13=isbn_search)

            #module_search = data['module']
            #if (module_search != ""):
            #    queryset = queryset.filter(tucanmodule__name__contains=module_search)

        return queryset

    def get_context_data(self, **kwargs):
        context = super(BookListView, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context

class AllBookListView(BookListView):
    queryset = Book.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super(AllBookListView, self).get_context_data(**kwargs)
        context['showtag'] = True
        return context

class BookView(DetailView):
    model = Book
    template_name = 'pyBuchaktion/book.html'
    context_object_name = 'book'
    pk_url_kwarg = 'book_id'
    book_order = False

    def post(self, request, *args, **kwargs):
        self.book_order = post_order_book(request, kwargs['book_id'])
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['book_order'] = self.book_order
        context['student'] = get_logged_in_student(self.request)
        if (context['student'] != None):
            context['orders'] = context['book'].order_set.filter(student=context['student'])
        return context

class ModulesView(VarPagedListView):
    model = TucanModule
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

    def get_context_data(self, **kwargs):
        context = super(ModulesView, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context

class ModuleView(DetailView):
    model = TucanModule
    template_name = 'pyBuchaktion/module.html'
    context_object_name = 'module'
    pk_url_kwarg = 'module_id'

class BaseOrderView(DetailView):
    context_object_name = 'order'
    pk_url_kwarg = 'order_id'

    def get_queryset(self):
        return Order.objects.filter(student=get_logged_in_student(self.request))

class OrderView(BaseOrderView):
    template_name = 'pyBuchaktion/order.html'
    
    def post(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse("pyBuchaktion:order_abort", kwargs=kwargs))

class OrderAbortView(BaseOrderView):
    template_name = 'pyBuchaktion/order_abort.html'

    def post(self, request, *args, **kwargs):
        try:
            action = request.POST['action']
            if (action == "Abort"):
                self.order_abort = post_abort_order(request, kwargs['order_id'])
                if (self.order_abort):
                    return HttpResponseRedirect(reverse("pyBuchaktion:account"))
            elif (action == "Cancel"):
                return HttpResponseRedirect(reverse("pyBuchaktion:order", kwargs['order_id']))
        except:
            pass

        return self.get(request, *args, **kwargs)


class AccountView(TemplateView):
    template_name = 'pyBuchaktion/account.html'

    def get_context_data(self, **kwargs):
        return {'student': get_logged_in_student(self.request)}
