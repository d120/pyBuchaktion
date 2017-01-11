from menus.base import Menu, NavigationNode
from menus.menu_pool import menu_pool
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

class PyBuchaktionMenu(Menu):

	def get_nodes(self, request):

		#n1 = NavigationNode(_('Buchaktion'), reverse('pyBuchaktion:index'), 1)
		n2_url = reverse('pyBuchaktion:books')
		n2_name = _('Bücher')
		n2 = NavigationNode(n2_name, n2_url, 1, attr={
			'page_title': n2_name,
		})
		n3_url = reverse('pyBuchaktion:books_all')
		n3_name = _('Alle Bücher')
		n3 = NavigationNode(n3_name, n3_url, 2, 1, attr={
			'page_title': n3_name,
		})

		nodes = [n2, n3]

		return nodes;

menu_pool.register_menu(PyBuchaktionMenu)