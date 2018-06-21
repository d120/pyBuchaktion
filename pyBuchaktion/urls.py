from django.conf.urls import include, url
from django.utils.translation import ugettext_lazy as _
from .views import *

app_name = 'pyBuchaktion'
urlpatterns = [
    url(r'^book/', include([
        url(r'^$', BookListView.as_view(), name = 'books'),
        url(r'^all/$', AllBookListView.as_view(), name = 'books_all'),
        url(r'^propose/$', BookProposeView.as_view(), name = 'book_propose'),
        url(r'^(?P<pk>\d*)/', include([
            url(r'^$',BookView.as_view(), name = 'book'),
            url(r'^order/$', BookOrderView.as_view(), name = 'book_order'),
        ])),
    ])),
    url(r'^module/', include([
        url(r'^(?P<pk>\d*)/', include([
            url(r'^$', ModuleDetailView.as_view(), name = 'module'),
            url(r'^addbook/$', LiteratureCreateView.as_view(), name = 'addbook'),
        ])),
        url(r'^search/', ModuleListView.as_view(), name='module_search'),
        url(r'^$', ModuleCategoriesView.as_view(), name = 'modules'),
    ])),
    url(r'^account/', include([
        url(r'^$', AccountView.as_view(), name = 'account'),
        url(r'^create/$', AccountCreateView.as_view(), name = 'account_create'),
        url(r'^delete/$', AccountDeleteView.as_view(), name = 'account_delete'),
    ])),
    url(r'^order/', include([
        url(r'^(?P<pk>\d*)/', include([
            url(r'^$', OrderDetailView.as_view(), name = 'order'),
            url(r'^abort/$', OrderAbortView.as_view(), name = 'order_abort'),
        ])),
    ])),
]
