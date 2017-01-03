from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _


class PyBuchaktionApphook(CMSApp):
    app_name = "pyBuchaktion"
    name = _("pyBuchaktion")

    def get_urls(self, page=None, language=None, **kwargs):
        return ["pyBuchaktion.urls"]


apphook_pool.register(PyBuchaktionApphook)
