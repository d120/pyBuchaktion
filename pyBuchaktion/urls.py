from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^book/$', BookListView.as_view(), name = 'books'),
    url(r'^book/all/$', AllBookListView.as_view(), name = 'books_all'),
    url(r'^book/(?P<pk>\d*)/$', BookView.as_view(), name = 'book'),
    url(r'^book/(?P<pk>\d*)/order/$', BookOrderView.as_view(), name = 'book_order'),
    url(r'^module/$', ModuleListView.as_view(), name='modules'),
    url(r'^module/(?P<pk>\d*)/$', ModuleDetailView.as_view(), name = 'module'),
    url(r'^account/$', AccountView.as_view(), name = 'account'),
    url(r'^order/(?P<pk>\d*)/$', OrderDetailView.as_view(), name = 'order'),
    url(r'^order/(?P<pk>\d*)/abort/$', OrderAbortView.as_view(), name = 'order_abort'),
]
