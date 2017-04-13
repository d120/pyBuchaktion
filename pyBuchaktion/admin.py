"""
    This module configures the administration views for this app.
    There is a class for each model that defines display columns
    and filters for the list view.
"""

from django.contrib.admin import ModelAdmin, register, helpers
from django.db.models import Count
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from django.template.response import TemplateResponse

from import_export.resources import ModelResource
from import_export.admin import ImportExportMixin

from .models import Book, Order, Student, OrderTimeframe, TucanModule, Semester
from .mixins import ForeignKeyImportResourceMixin
from .data import net_library_csv

class BookResource(ModelResource):
    class Meta:
        model = Book
        import_id_fields = (
            'isbn_13',
        )
        fields = import_id_fields + (
            'title',
            'state',
            'author',
            'price',
            'publisher',
            'year',
        )

@register(Book)
class BookAdmin(ImportExportMixin, ModelAdmin):

    """
        The book admin displays title, author and isbn of a book,
        as well as the number of order for this book.
    """

    resource_class = BookResource

    # The columns that are displayed in the list view
    list_display = (
        'title',
        'author',
        'isbn_13',
        'number_of_orders',
    )

    # The keys that the list can be filtered by
    list_filter = (
        'state',
    )

    # Annotate the queryset with the number of orders.
    def get_queryset(self, request):
        qs = super(BookAdmin, self).get_queryset(request)
        qs = qs.annotate(Count('order'))
        return qs

    # The number of orders for this book
    def number_of_orders(self, book):
        return book.order__count

    number_of_orders.admin_order_field = 'order__count'
    number_of_orders.short_description = _("orders")


class OrderResource(ForeignKeyImportResourceMixin, ModelResource):
    class Meta:
        model = Order
        import_id_fields = (
            'book__isbn_13',
            'student__tuid_user__uid',
            'order_timeframe__id',
        )
        fields = (
            'status',
        ) + import_id_fields

@register(Order)
class OrderAdmin(ImportExportMixin, ModelAdmin):

    """
        The admin for the orders, displaying the title of the ordered book,
        the student ordering the book and the timeframe.
    """

    resource_class = OrderResource

    # The columns that are displayed
    list_display = (
        'id',
        'book_title',
        'student',
        'timeframe',
    )

    # The keys that the list can be filtered by
    list_filter = (
        'status',
        'book__state',
        'order_timeframe',
    )

    # The actions that can be triggered on orders
    actions = [
        "export",
        "order_selected",
        "mark_arrived_selected",
        "reject_selected",
    ]

    # The title of the book to be ordered
    def book_title(self, order):
        return order.book.title

    book_title.short_description = _("title")

    # The timeframe to which this order belongs
    def timeframe(self, order):
        start = _("{:%Y-%m-%d}").format(order.order_timeframe.start_date)
        end = _("{:%Y-%m-%d}").format(order.order_timeframe.end_date)
        return _("%(start)s to %(end)s") % {'start': start, 'end': end}

    timeframe.short_description = _("order timeframe")

    # The admin action for exporting to custom CSV
    def export(self, request, queryset):
        response = HttpResponse(net_library_csv(queryset), content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="export.csv"'
        return response

    export.short_description = _("Export orders to custom CSV")

    # The admin action for rejecting all selected orders at once.
    def reject_selected(self, request, queryset):
        if request.POST.get('_proceed'):
            for order in queryset:
                order.status = Order.REJECTED
                hint = request.POST.get('hint')
                if hint:
                    order.hint = hint
                else:
                    order.hint = ""
                order.save()
        elif not request.POST.get('_cancel'):
            context = dict(
                self.admin_site.each_context(request),
                title = _("Rejecting orders: Are you sure?"),
                queryset = queryset,
                action_checkbox_name = helpers.ACTION_CHECKBOX_NAME,
            )
            return TemplateResponse(request, 'pyBuchaktion/admin/order_reject_selected.html', context)

    reject_selected.short_description = _("reject selected orders")

    # The admin action for marking all selected orders as arrived.
    def mark_arrived_selected(self, request, queryset):
        if request.POST.get('_proceed'):
            for order in queryset:
                order.status = Order.ARRIVED
                hint = request.POST.get('hint')
                if hint:
                    order.hint = hint
                else:
                    order.hint = ""
                order.save()
        elif not request.POST.get('_cancel'):
            context = dict(
                self.admin_site.each_context(request),
                title = _("Marking as arrived: Are you sure?"),
                queryset = queryset,
                action_checkbox_name = helpers.ACTION_CHECKBOX_NAME,
            )
            return TemplateResponse(request, 'pyBuchaktion/admin/order_mark_arrived_selected.html', context)

    mark_arrived_selected.short_description = _("mark selected orders as arrived")

    # The admin action for ordering the selected books
    def order_selected(self, request, queryset):
        if request.POST.get('_proceed'):
            for order in queryset:
                order.status = Order.ORDERED
                hint = request.POST.get('hint')
                if hint:
                    order.hint = hint
                else:
                    order.hint = ""
                order.save()
            context = dict(
                self.admin_site.each_context(request),
                title = _("Ordering: CSV-Export"),
                queryset = queryset,
                opts = self.opts,
                action_checkbox_name = helpers.ACTION_CHECKBOX_NAME,
            )
            return TemplateResponse(request, 'pyBuchaktion/admin/order_order_selected_csv.html', context)
        elif request.POST.get('_ok'):
            pass # return to list view
        elif not request.POST.get('_cancel'):
            context = dict(
                self.admin_site.each_context(request),
                title = _("Ordering: Are you sure?"),
                queryset = queryset,
                opts = self.opts,
                action_checkbox_name = helpers.ACTION_CHECKBOX_NAME,
            )
            return TemplateResponse(request, 'pyBuchaktion/admin/order_order_selected.html', context)

    order_selected.short_description = _("order selected orders")

@register(Student)
class StudentAdmin(ModelAdmin):

    """
        The admin for students.
    """

    ordering = (
        'id',
    )

    # The columns that are displayed
    list_display = (
        'id',
        'tuid_user',
        'library_id',
    )

    # The columns that are displayed as links
    list_display_links = (
        'tuid_user',
    )

@register(OrderTimeframe)
class OrderTimeframeAdmin(ModelAdmin):

    """
        The admin for order timeframes displays the start and end dates and
        the semester the timeframe belongs to.
    """

    # The columns that are displayed in the list view
    list_display = (
        'end_date',
        'start_date',
        'semester',
    )

@register(Semester)
class SemesterAdmin(ModelAdmin):

    """
        The admin for a semester.
    """

    #radio_fields = {"season": admin.VERTICAL}
    pass

@register(TucanModule)
class ModuleAdmin(ModelAdmin):

    """
        The admin for a module displays the name and module id.
    """

    list_display = (
        'name',
        'module_id',
    )
