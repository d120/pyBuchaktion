from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^book/$', BookListView.as_view(), name = 'books'),
    url(r'^book/all/$', AllBookListView.as_view(), name = 'books_all'),
    url(r'^book/(?P<book_id>\d*)/$', BookView.as_view(), name = 'book'),
    url(r'^module/$', ModuleListView.as_view(), name='modules'),
    url(r'^module/(?P<module_id>\d*)/$', ModuleDetailView.as_view(), name = 'module'),
    url(r'^account/$', AccountView.as_view(), name = 'account'),
    url(r'^order/(?P<order_id>\d*)/$', OrderDetailView.as_view(), name = 'order'),
    url(r'^order/(?P<order_id>\d*)/abort/$', OrderAbortView.as_view(), name = 'order_abort'),
]
