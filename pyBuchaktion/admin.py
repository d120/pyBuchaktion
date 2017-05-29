"""
    This module configures the administration views for this app.
    There is a class for each model that defines display columns
    and filters for the list view.
"""

from django.contrib.admin import ModelAdmin, register, helpers
from django.db.models import Count
from django.utils.translation import ugettext_lazy as _
from django.utils.text import Truncator
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.core.mail.message import EmailMessage

from import_export.resources import ModelResource
from import_export.admin import ImportExportMixin
from import_export.widgets import ManyToManyWidget
from import_export.fields import Field

from .models import Book, Order, Student, OrderTimeframe, Module, Semester, ModuleCategory, DisplayMessage
from .mixins import ForeignKeyImportResourceMixin
from .data import net_library_csv
from .mail import OrderAcceptedMessage, OrderArrivedMessage, OrderRejectedMessage, CustomMessage

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
        as well as the number of orders for this book.
    """

    resource_class = BookResource

    # The columns that are displayed in the list view
    list_display = (
        'title',
        'author',
        'isbn_13',
        'number_of_orders',
        'state',
    )

    # The keys that the list can be filtered by
    list_filter = (
        'state',
    )

    actions = [
        'accept_selected',
    ]

    # Annotate the queryset with the number of orders.
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(Count('order'))
        return qs

    # The number of orders for this book
    def number_of_orders(self, book):
        return book.order__count

    number_of_orders.admin_order_field = 'order__count'
    number_of_orders.short_description = _("orders")

    def accept_selected(self, request, queryset):
        queryset.values("id").update(state=Book.ACCEPTED)

    accept_selected.short_description = _("Accept selected books")


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
        'status',
    )

    # The keys that the list can be filtered by
    list_filter = (
        'status',
        'book__state',
        'order_timeframe',
    )

    search_fields = [
        'book__title'
    ]

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
            hint = request.POST.get('hint')
            sendmails = '_sendmails' in request.POST
            for order in queryset:
                order.status = Order.REJECTED
                order.hint = hint
                order.save()
                if sendmails:
                    email = OrderRejectedMessage(order)
                    email.send()
        elif not request.POST.get('_cancel'):
            context = dict(
                self.admin_site.each_context(request),
                title = _("Rejecting orders: Are you sure?"),
                intro = _("The follwing orders will be rejected. Are you sure?"),
                action = 'reject_selected',
                queryset = queryset,
                opts = self.opts,
                action_checkbox_name = helpers.ACTION_CHECKBOX_NAME,
            )
            return TemplateResponse(request, 'pyBuchaktion/admin/order_modify_bulk.html', context)

    reject_selected.short_description = _("reject selected orders")

    # The admin action for marking all selected orders as arrived.
    def mark_arrived_selected(self, request, queryset):
        if request.POST.get('_proceed'):
            sendmails = '_sendmails' in request.POST
            hint = request.POST.get('hint', "")
            for order in queryset:
                order.status = Order.ARRIVED
                order.hint = hint
                order.save()
                if sendmails:
                    email = OrderArrivedMessage(order)
                    email.send()
        elif not request.POST.get('_cancel'):
            context = dict(
                self.admin_site.each_context(request),
                title = _("Marking as arrived: Are you sure?"),
                intro = _("The follwing orders will be marked as having been delivered. Are you sure?"),
                action = 'mark_arrived_selected',
                queryset = queryset,
                opts = self.opts,
                action_checkbox_name = helpers.ACTION_CHECKBOX_NAME,
            )
            return TemplateResponse(request, 'pyBuchaktion/admin/order_modify_bulk.html', context)

    mark_arrived_selected.short_description = _("mark selected orders as arrived")

    # The admin action for ordering the selected books
    def order_selected(self, request, queryset):
        if request.POST.get('_proceed'):
            sendmails = '_sendmails' in request.POST
            hint = request.POST.get('hint', "")
            for order in queryset:
                order.status = Order.ORDERED
                order.hint = hint
                order.save()
                if sendmails:
                    email = OrderAcceptedMessage(order)
                    email.send()
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
                intro = _("The following orders will be marked as ordered. Are you sure?"),
                action = 'order_selected',
                queryset = queryset,
                opts = self.opts,
                action_checkbox_name = helpers.ACTION_CHECKBOX_NAME,
            )
            return TemplateResponse(request, 'pyBuchaktion/admin/order_modify_bulk.html', context)

    order_selected.short_description = _("order selected orders")

@register(Student)
class StudentAdmin(ModelAdmin):

    """
        The admin for students.
    """

    # The columns that are displayed
    list_display = (
        'id',
        'tuid_user',
        'email',
        'has_library_id',
        'language',
        'number_of_orders',
    )

    # The columns that are displayed as links
    list_display_links = (
        'tuid_user',
    )

    actions = [
        'sendmail',
    ]

    readonly_fields = (
        'tuid_user',
    )

    # Annotate the queryset with the number of orders.
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(Count('order'))
        return qs

    # The number of orders for this book
    def number_of_orders(self, student):
        return student.order__count

    number_of_orders.admin_order_field = 'order__count'
    number_of_orders.short_description = _("orders")

    def has_library_id(self, student):
        return True if student.library_id else False
    has_library_id.boolean = True
    has_library_id.short_description = _("library id")

    # The admin action for ordering the selected books
    def sendmail(self, request, queryset):
        if request.POST.get('_proceed'):
            text = request.POST.get('text', "")
            if len(text) > 0:
                for student in queryset:
                    email = CustomMessage(student, text)
                    email.send()

        elif not request.POST.get('_cancel'):
            context = dict(
                self.admin_site.each_context(request),
                title = _("Send notification email"),
                intro = _("Write a custom notification here, which will be sent to all selected students"),
                action = 'sendmail',
                queryset = queryset,
                opts = self.opts,
                action_checkbox_name = helpers.ACTION_CHECKBOX_NAME,
            )
            return TemplateResponse(request, 'pyBuchaktion/admin/student_sendmail.html', context)

    sendmail.short_description = _("send mail to students")


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


class ModuleResource(ForeignKeyImportResourceMixin, ModelResource):
    author = Field(
        column_name = 'books',
        attribute = 'literature',
        widget = ManyToManyWidget(
            Book,
            separator = '|',
            field = 'isbn_13',
        ),
    )

    class Meta:
        model = Module
        import_id_fields = (
            'module_id',
            'last_offered__year',
            'last_offered__season',
        )
        fields = import_id_fields + (
            'name',
            'books',
        )


@register(Module)
class ModuleAdmin(ImportExportMixin, ModelAdmin):

    """
        The admin for a module displays the name and module id.
    """

    resource_class = ModuleResource

    list_display = (
        'name',
        'module_id',
        'category',
    )

    search_fields = [
        'name',
        'module_id',
    ]

    list_filter = (
        'category',
    )


@register(ModuleCategory)
class ModuleCategoryAdmin(ModelAdmin):

    list_display = (
        'id',
        'name_de',
        'name_en',
    )

    list_display_links = (
        'name_de',
    )

    fieldsets = (
        ('Namen', {
            'fields': (('name_de', 'name_en'),)
        }),
    )


class DisplayMessageResource(ModelResource):

    class Meta:
        model = DisplayMessage
        import_id_fields = 'key',
        fields = import_id_fields + (
            'text_de',
            'text_en',
        )

@register(DisplayMessage)
class DisplayMessageAdmin(ImportExportMixin, ModelAdmin):

    """
        The book admin displays title, author and isbn of a book,
        as well as the number of orders for this book.
    """

    resource_class = DisplayMessageResource

    list_display = (
        'key',
        'trunc_de',
        'trunc_en',
    )

    def trunc_de(self, obj):
        return Truncator(obj.text_de).chars(60)
    trunc_de.short_description = _("german text")

    def trunc_en(self, obj):
        return Truncator(obj.text_en).chars(60)
    trunc_en.short_description = _("english text")
