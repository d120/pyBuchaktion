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
    url(r'^order/(?P<order_id>\d*)/abort/$', OrderAbortView.as_view(), name = 'order_abort'),
    url(r'^api$', ApiListView.as_view(), name = 'api'),
    url(r'^api/books$', BooksApiListView.as_view(), name = 'api/books'),
    url(r'^api/books/(?P<book_id>\d+)$', BookApiDetailView.as_view(), name = 'api/books/<book_id>'),
    url(r'^api/modules/(?P<module_id>\d+)$', ModuleApiDetailView.as_view(), name='api/modules/<module_id>'),
    url(r'^api/orders/(?P<order_id>\d+)$', OrderApiDetailView.as_view(), name='api/orders/<order_id>'),
    url(r'^api/account$', AccountApiDetailView.as_view(), name='api/account'),
    url(r'^api/account/orders$', OrderApiListView.as_view(), name='api/account/orders'),
]
