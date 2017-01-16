from django.conf.urls import url

from . import views
from .views import BookListView, AllBookListView, BookView, ModulesView, ModuleView

urlpatterns = [
    url(r'^books/$', BookListView.as_view(), name = 'books'),
    url(r'^books/all/$', AllBookListView.as_view(), name = 'books_all'),
    url(r'^book/(?P<book_id>\d*)/$', BookView.as_view(), name = 'book'),
    url(r'^modules/$', ModulesView.as_view(), name='modules'),
    url(r'^module/(?P<module_id>\d*)/$', ModuleView.as_view(), name = 'module'),
]
