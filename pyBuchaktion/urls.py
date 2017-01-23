from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^books/$', BookListView.as_view(), name = 'books'),
    url(r'^books/all/$', AllBookListView.as_view(), name = 'books_all'),
    url(r'^book/(?P<book_id>\d*)/$', BookView.as_view(), name = 'book'),
    url(r'^modules/$', ModulesView.as_view(), name='modules'),
    url(r'^module/(?P<module_id>\d*)/$', ModuleView.as_view(), name = 'module'),
    url(r'^account/$', AccountView.as_view(), name = 'account'),
    url(r'^order/(?P<order_id>\d*)/$', OrderView.as_view(), name = 'order'),
]
