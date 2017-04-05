"""
    This module configures the administration views for this app.
    There is a class for each model that defines display columns
    and filters for the list view.
"""

from django.contrib import admin
from django.db.models import Count
from django.utils.translation import ugettext_lazy as _
#from import_export import resources
#from import_export.admin import ImportExportActionModelAdmin
from django.http import HttpResponse
import io
import csv

from . import models

@admin.register(models.Book)
class BookAdmin(admin.ModelAdmin):

    """
        The book admin displays title, author and isbn of a book,
        as well as the number of order for this book.
    """

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

#class OrderResource(resources.ModelResource):
#
#    class Meta:
#        model = models.Order

@admin.register(models.Order)
#class OrderAdmin(ImportExportActionModelAdmin):
class OrderAdmin(admin.ModelAdmin):

    """
        The admin for the orders, displaying the title of the ordered book,
        the student ordering the book and the timeframe.
    """

    # The columns that are displayed
    list_display = (
        'book_title',
        'student',
        'timeframe',
    )

    # The keys that the list can be filtered by
    list_filter = (
        'status',
        'order_timeframe',
    )

    # The actions that can be triggered on orders
    actions = ["export"]

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

        out_stream = io.StringIO()
        writer = csv.writer(out_stream, delimiter='|', quotechar="\"", quoting=csv.QUOTE_MINIMAL)
        for order in queryset:
            array = [
                order.student.library_id,
                order.book.author,
                order.book.title,
                order.book.publisher,
                order.book.year,
                order.book.isbn_13
            ]
            writer.writerow(array)

        response = HttpResponse(out_stream.getvalue(), content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="export.csv"'
        return response

    export.short_description = _("Export orders to custom CSV")

@admin.register(models.Student)
class StudentAdmin(admin.ModelAdmin):

    """
        The admin for students.
    """

    # The columns that are displayed
    list_display = (
        'id',
        'library_id',
    )

    # The columns that are displayed as links
    list_display_links = (
        'id',
        'library_id',
    )

@admin.register(models.OrderTimeframe)
class OrderTimeframeAdmin(admin.ModelAdmin):

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

@admin.register(models.Semester)
class SemesterAdmin(admin.ModelAdmin):

    """
        The admin for a semester.
    """

    #radio_fields = {"season": admin.VERTICAL}
    pass

@admin.register(models.TucanModule)
class ModuleAdmin(admin.ModelAdmin):

    """
        The admin for a module displays the name and module id.
    """

    list_display = (
        'name',
        'module_id',
    )
