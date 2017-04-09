from menus.base import Menu, NavigationNode, Modifier
from menus.menu_pool import menu_pool
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from pyBuchaktion.models import Book, TucanModule, Order
from .data import get_logged_in_student

class PyBuchaktionMenu(Menu):

    def get_nodes(self, request):

        #n1 = NavigationNode(_('Buchaktion'), reverse('pyBuchaktion:index'), 1)
        n2 = NavigationNode(_('Books'), reverse('pyBuchaktion:books'), 5001)
        n3 = NavigationNode(_('All Books'), reverse('pyBuchaktion:books_all'), 5002, 5001)
        n4 = NavigationNode(_('Modules'), reverse('pyBuchaktion:modules'), 5004)
        nodes = [n2, n3, n4]

        if (get_logged_in_student(request) != None):
            nodes += [NavigationNode(_("Account"), reverse('pyBuchaktion:account'), 5006),]

        match = request.resolver_match
        if match.url_name in ['book', 'book_order']:
            book_id = match.kwargs['pk']
            book = Book.objects.get(pk=book_id)
            if book:
                nodes += [
                    NavigationNode(
                        _(book.title),
                        reverse(
                            'pyBuchaktion:book',
                            kwargs = {
                                'pk': book_id
                            },
                        ), 5003, 5001,
                        attr = {
                            'breadcrumb_only': True
                        }
                    ),
                ]
                if match.url_name == 'book_order':
                    nodes += [
                        NavigationNode(
                            _("Order book"),
                            reverse(
                                'pyBuchaktion:book_order',
                                kwargs = {
                                    'pk': book_id
                                },
                            ), 5012, 5003,
                            attr = {
                                'breadcrumb_only': True
                            }
                        ),
                    ]

        elif match.url_name == 'module':
            module_id = match.kwargs['pk']
            module = TucanModule.objects.get(pk=module_id)
            if module:
                nodes += [
                    NavigationNode(
                        _(module.name),
                        reverse(
                            'pyBuchaktion:module',
                            kwargs={
                                'pk': module_id
                            },
                        ), 5005, 5004,
                        attr = {
                            'breadcrumb_only': True
                        }
                    ),
                ]
        elif match.url_name in ('order', 'order_abort'):
            order_id = match.kwargs['pk']
            order = Order.objects.get(pk=order_id)
            if order:
                nodes += [
                    NavigationNode(
                        _("Order #%s") % order_id,
                        reverse(
                            'pyBuchaktion:order',
                            kwargs = {
                                'pk': order_id
                            },
                        ), 5007, 5006,
                        attr = {
                            'breadcrumb_only': True
                        }
                    ),
                ]

        return nodes;

menu_pool.register_menu(PyBuchaktionMenu)

class PyBuchaktionModifier(Modifier):
    """
    Modifies the navigation, so that node with attribute breadcrumb_only are only
    returned when in breadcrumb mode
    """
    def modify(self, request, nodes, namespace, root_id, post_cut, breadcrumb):
        if not breadcrumb and not post_cut:
            for node in nodes:
                if node.attr.get("breadcrumb_only"):
                    node.visible = False
        return nodes

menu_pool.register_modifier(PyBuchaktionModifier)
