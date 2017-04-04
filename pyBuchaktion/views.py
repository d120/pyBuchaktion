from django.views.generic import ListView, DetailView, TemplateView, View
from django.views.generic.base import ContextMixin
from django.views.generic.list import MultipleObjectMixin
from django.views.generic.detail import SingleObjectMixin
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.core.serializers.python import Serializer
from django.http import HttpResponseRedirect, HttpResponse
from .data import get_logged_in_student, post_order_book, post_abort_order, _model_to_dict
from .forms import BookSearchForm, ModuleSearchForm
from .models import Book, TucanModule, Order


class VarPagedMultipleObjectMixin(MultipleObjectMixin):
    paginate_by_default = 10
    paginate_by_options = [10, 25, 50, 100]

    def get_paginate_by(self, queryset):
        opts = self.request.GET
        if 'limit' in opts:
            limit = int(self.request.GET['limit'])
            if (limit in self.paginate_by_options):
                self.paginate_by = limit
        else:
            self.paginate_by = self.paginate_by_default

        return self.paginate_by


class VarPagedListView(ListView, VarPagedMultipleObjectMixin):

    def get_context_data(self, **kwargs):
        context = super(VarPagedListView, self).get_context_data(**kwargs)
        context['get_params'] = self.request.GET
        context['limit'] = self.paginate_by
        context['limit_options'] = self.paginate_by_options
        context['limit_default'] = self.paginate_by_default
        return context


class FormContextMixin(ContextMixin):

    def get_context_data(self, **kwargs):
        context = super(FormContextMixin, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context


class BookList(VarPagedMultipleObjectMixin):
    queryset = Book.objects.filter(state=Book.ACCEPTED)

    def get_queryset(self):
        self.form = BookSearchForm(self.request.GET)
        queryset = super(BookList, self).get_queryset()

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
            # if (module_search != ""):
            #    queryset = queryset.filter(tucanmodule__name__contains=module_search)

        return queryset


class AllBooksList(BookList):
    queryset = Book.objects.all()


class BookListView(BookList, VarPagedListView, FormContextMixin):
    template_name = 'pyBuchaktion/books/active_list.html'
    context_object_name = 'books'


class AllBookListView(AllBooksList, BookListView):
    template_name = 'pyBuchaktion/books/all_list.html'

    def get_context_data(self, **kwargs):
        context = super(AllBookListView, self).get_context_data(**kwargs)
        context['showtag'] = True
        return context


class BookDetail(SingleObjectMixin):
    model = Book
    pk_url_kwarg = 'book_id'
    book_order = False

    def post(self, request, *args, **kwargs):
        self.book_order = post_order_book(request, kwargs['book_id'])
        return self.get(request, *args, **kwargs)


class BookView(DetailView, BookDetail):
    template_name = 'pyBuchaktion/book.html'
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['book_order'] = self.book_order
        context['student'] = get_logged_in_student(self.request)
        if (context['student'] is not None):
            context['orders'] = context['book'].order_set.filter(
                student=context['student'])
        return context


class ModuleList(MultipleObjectMixin):
    model = TucanModule

    def get_queryset(self):
        self.form = ModuleSearchForm(self.request.GET)
        queryset = TucanModule.objects.all()

        if (self.form.is_valid()):
            data = self.form.cleaned_data

            queryset = queryset.filter(name__contains=data['name'])

            if (data['module_id'] != ""):
                queryset = queryset.filter(module_id=data['module_id'])

        return queryset


class ModulesView(VarPagedListView, ModuleList, FormContextMixin):
    template_name = 'pyBuchaktion/modules.html'
    context_object_name = 'modules'


class ModuleDetail(SingleObjectMixin):
    model = TucanModule
    pk_url_kwarg = 'module_id'


class ModuleView(DetailView, ModuleDetail):
    template_name = 'pyBuchaktion/module.html'
    context_object_name = 'module'


class OrderList(MultipleObjectMixin):

    def get_queryset(self):
        return Order.objects.filter(student=get_logged_in_student(self.request))


class OrderDetail(SingleObjectMixin):
    pk_url_kwarg = 'order_id'

    def get_queryset(self):
        return Order.objects.filter(student=get_logged_in_student(self.request))


class BaseOrderView(DetailView, OrderDetail):
    context_object_name = 'order'


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
                self.order_abort = post_abort_order(
                    request, kwargs['order_id'])
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


class ObjectSerializer(Serializer):

    def end_object(self, obj):
        self._current['id'] = obj._get_pk_val()
        self.objects.append(self._current)


class ApiListView(View):
    fields = None
    queryset = {}
    wrap_name = None

    def wrap(self, data):
        if (self.wrap_name is not None):
            return {self.wrap_name: data}
        return data

    def get_object_list(self):
        return self.get_queryset()

    def get(self, request, *args, **kwargs):
        serializer = ObjectSerializer()
        data = serializer.serialize(
            self.get_object_list(),
            use_natural_foreign_keys=True,
            fields=self.fields,
        )
        json_encoder = DjangoJSONEncoder(indent=2)
        json = json_encoder.encode(self.wrap(data))
        return HttpResponse(json, content_type='application/json')


class ApiDetailView(View):
    object = {}
    wrap_name = None

    def wrap(self, data):
        if (self.wrap_name is not None):
            return {self.wrap_name: data}
        return data

    def get_object(self, queryset=None):
        return self.object

    def get(self, request, *args, **kwargs):
        json_encoder = DjangoJSONEncoder(indent=2)
        json = json_encoder.encode(
            self.wrap(_model_to_dict(self.get_object())))
        return HttpResponse(json, content_type='application/json')


class PagedApiListView(ApiListView, MultipleObjectMixin):
    is_paginated = False
    paginator = None
    page = None
    object_list = {}

    def wrap(self, data):
        wrapped = super(PagedApiListView, self).wrap(data)
        if (self.is_paginated):
            wrapped["total"] = self.paginator.count
        return wrapped

    def get_object_list(self):
        queryset = self.get_queryset()
        paginate_by = self.get_paginate_by(queryset)
        data = self.paginate_queryset(queryset, paginate_by)
        self.paginator = data[0]
        self.page = data[1]
        self.object_list = data[2]
        self.is_paginated = data[3]
        return self.object_list


class VarPagedApiListView(PagedApiListView, VarPagedMultipleObjectMixin):
    pass


class BooksApiListView(BookList, VarPagedApiListView):
    fields = ('isbn_13', 'title', 'author')
    wrap_name = "books"


class BookApiDetailView(BookDetail, ApiDetailView):
    wrap_name = 'book'


class ModuleApiDetailView(ModuleDetail, ApiDetailView):
    wrap_name = 'module'


class OrderApiDetailView(OrderDetail, ApiDetailView):
    wrap_name = 'order'


class OrderApiListView(OrderList, ApiListView):
    wrap_name = 'orders'


class AccountApiDetailView(ApiDetailView):
    wrap_name = 'account'

    def get_object(self, queryset=None):
        return get_logged_in_student(self.request)
