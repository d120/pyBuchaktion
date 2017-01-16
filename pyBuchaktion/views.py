from django.views.generic import ListView, DetailView
from pyBuchaktion.models import Book, TucanModule

class BookListView(ListView):
    queryset = Book.objects.filter(state=Book.ACCEPTED)
    template_name = 'pyBuchaktion/books.html'
    context_object_name = 'books'
    paginate_by = 10

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

class ModulesView(ListView):
    model = TucanModule
    template_name = 'pyBuchaktion/modules.html'
    context_object_name = 'modules'

class ModuleView(DetailView):
    model = TucanModule
    template_name = 'pyBuchaktion/module.html'
    context_object_name = 'module'
    pk_url_kwarg = 'module_id'
