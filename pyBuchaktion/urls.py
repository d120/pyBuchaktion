from django.conf.urls import url

from . import views

urlpatterns = [
    #url(r'^$', views.index, name = 'index'),
    url(r'^books/$', views.books, name = 'books'),
    url(r'^books/all/$', views.books_all, name = 'books_all'),
    url(r'^books/(?P<book_id>\d*)/$', views.book, name = 'book'),
    url(r'^modules/$', views.modules, name='modules'),
    url(r'^modules/(?P<module_id>\d*)/$', views.module, name = 'module'),
]
