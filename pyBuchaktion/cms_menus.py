from menus.base import Menu, NavigationNode, Modifier
from menus.menu_pool import menu_pool
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from pyBuchaktion.models import Book, TucanModule, Order
from .data import get_logged_in_student

class PyBuchaktionMenu(Menu):

    def get_nodes(self, request):

        #n1 = NavigationNode(_('Buchaktion'), reverse('pyBuchaktion:index'), 1)
        n2 = NavigationNode(_('Books'), reverse('pyBuchaktion:books'), 1)
        n3 = NavigationNode(_('All Books'), reverse('pyBuchaktion:books_all'), 2, 1)
        n4 = NavigationNode(_('Modules'), reverse('pyBuchaktion:modules'), 4)
        nodes = [n2, n3, n4]

        if (get_logged_in_student(request) != None):
            nodes += [NavigationNode(_("Account"), reverse('pyBuchaktion:account'), 6),]

        match = request.resolver_match
        if match.url_name == 'book':
            book_id = match.kwargs['book_id']
            book = Book.objects.get(pk=book_id)
            if book:
                nBook = [NavigationNode(_(book.title), reverse(
                    'pyBuchaktion:book', kwargs={'book_id': book_id}
                ), 3, 1),]
                nodes += nBook
        elif match.url_name == 'module':
            module_id = match.kwargs['module_id']
            module = TucanModule.objects.get(pk=module_id)
            if module:
                nModule = [NavigationNode(_(module.name), reverse(
                    'pyBuchaktion:module', kwargs={ 'module_id': module_id }
                ), 5, 4),]
                nodes += nModule
        elif match.url_name in ('order', 'order_abort'):
            order_id = match.kwargs['order_id']
            order = Order.objects.get(pk=order_id)
            if order:
                nOrder = [NavigationNode(_("Order #%s") % order_id, reverse(
                    'pyBuchaktion:order', kwargs={ 'order_id': order_id }
                ), 7, 6),]
                nodes += nOrder

        return nodes;

menu_pool.register_menu(PyBuchaktionMenu)
