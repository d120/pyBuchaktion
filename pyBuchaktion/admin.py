"""
This module configures the administration views for this app.
There is a class for each model that defines display columns
and filters for the list view.
"""

import re
import isbnlib

from django.contrib.admin import ModelAdmin, register, helpers
from django.db.models import Count
from django.db.models.query import Prefetch
from django.utils.translation import ugettext_lazy as _
from django.utils.text import Truncator
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.core.mail.message import EmailMessage

from import_export.resources import ModelResource
from import_export.admin import ImportExportMixin
from import_export.widgets import ManyToManyWidget, ForeignKeyWidget, Widget
from import_export.fields import Field

from .models import Book, Order, Student, OrderTimeframe, Module, Literature, Semester, ModuleCategory, DisplayMessage
from .mixins import ForeignKeyImportResourceMixin
from .data import net_library_csv
from .mail import OrderAcceptedMessage, OrderArrivedMessage, OrderRejectedMessage, CustomMessage


class BookResource(ModelResource):
    """
    The django-import-export resource used to configure
    the fields for import and export.
    """

    def init_instance(self, row):
        return Book(state=Book.PROPOSED)

    class Meta:
        model = Book
        import_id_fields = (
            'isbn_13',
        )

        fields = import_id_fields + (
            'title',
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
        'title_truncated',
        'author_truncated',
        'isbn_pretty',
        'number_of_orders',
        'state',
    )

    # The keys that the list can be filtered by
    list_filter = (
        'state',
    )

    search_fields = (
        'title',
        'author',
        'isbn_13',
    )

    actions = [
        'accept_selected',
    ]

    fieldsets = [
        ("", {
            'fields': (('title',), ('author',), ('publisher', 'year'), ('isbn_13', 'price', 'state'), ('note',))
        }),
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
    number_of_orders.short_description = _("# ord.")

    def accept_selected(self, request, queryset):
        queryset.values("id").update(state=Book.ACCEPTED)

    accept_selected.short_description = _("Accept selected books")

    def title_truncated(self, book):
        return Truncator(book.title).chars(40)

    title_truncated.admin_order_field = 'title'
    title_truncated.short_description = _("title")

    def author_truncated(self, book):
        return Truncator(book.author).chars(40)

    author_truncated.admin_order_field = 'author'
    author_truncated.short_description = _("author")

    def isbn_pretty(self, book):
        try:
            return isbnlib.mask(book.isbn_13)
        except:
            return book.isbn_13

    isbn_pretty.admin_order_field = 'isbn_13'
    isbn_pretty.short_description = _("ISBN-13")


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

    fieldsets = (
        (_('General'), {
            'fields': (('book',), ('student',), ('status', 'order_timeframe'))
        }),
        (_('Details'), {
            'fields': (('hint',),)
        }),
    )

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
            errors = []
            hint = request.POST.get('hint')
            sendmails = '_sendmails' in request.POST
            for order in queryset:
                order.status = Order.REJECTED
                order.hint = hint
                order.save()
                if sendmails:
                    email = OrderRejectedMessage(order)
                    try:
                        email.send()
                    except Exception:
                        errors += [order.student.email]
            if len(errors) > 0:
                context = dict(
                    self.admin_site.each_context(request),
                    title=_("Errors"),
                    intro=_("The following emails could not be sent"),
                    errors=errors
                )
                return TemplateResponse(request, 'pyBuchaktion/admin/order_error.html', context)
        elif not request.POST.get('_cancel'):
            context = dict(
                self.admin_site.each_context(request),
                title=_("Rejecting orders: Are you sure?"),
                intro=_("The follwing orders will be rejected. Are you sure?"),
                action='reject_selected',
                queryset=queryset,
                opts=self.opts,
                action_checkbox_name=helpers.ACTION_CHECKBOX_NAME,
            )
            return TemplateResponse(request, 'pyBuchaktion/admin/order_modify_bulk.html', context)

    reject_selected.short_description = _("reject selected orders")

    # The admin action for marking all selected orders as arrived.
    def mark_arrived_selected(self, request, queryset):
        if request.POST.get('_proceed'):
            errors=[]
            sendmails = '_sendmails' in request.POST
            hint = request.POST.get('hint', "")
            for order in queryset:
                order.status = Order.ARRIVED
                order.hint = hint
                order.save()
                if sendmails:
                    email = OrderArrivedMessage(order)
                    try:
                        email.send()
                    except Exception:
                        errors += [order.student.email]
            if len(errors) > 0:
                context = dict(
                    self.admin_site.each_context(request),
                    title=_("Errors"),
                    intro=_("The following emails could not be sent"),
                    errors=errors
                )
                return TemplateResponse(request, 'pyBuchaktion/admin/order_error.html', context)
        elif not request.POST.get('_cancel'):
            context = dict(
                self.admin_site.each_context(request),
                title=_("Marking as arrived: Are you sure?"),
                intro=_("The follwing orders will be marked as having been delivered. Are you sure?"),
                action='mark_arrived_selected',
                queryset=queryset,
                opts=self.opts,
                action_checkbox_name=helpers.ACTION_CHECKBOX_NAME,
            )
            return TemplateResponse(request, 'pyBuchaktion/admin/order_modify_bulk.html', context)

    mark_arrived_selected.short_description = _("mark selected orders as arrived")

    # The admin action for ordering the selected books
    def order_selected(self, request, queryset):
        if request.POST.get('_proceed'):
            errors=[]
            sendmails = '_sendmails' in request.POST
            hint = request.POST.get('hint', "")
            for order in queryset:
                order.status = Order.ORDERED
                order.hint = hint
                order.save()
                if sendmails:
                    email = OrderAcceptedMessage(order)
                    try:
                        email.send()
                    except Exception:
                        errors += [order.student.email]
            context = dict(
                self.admin_site.each_context(request),
                title=_("Ordering: CSV-Export"),
                queryset=queryset,
                opts=self.opts,
                errors=[],
                action_checkbox_name=helpers.ACTION_CHECKBOX_NAME,
            )
            return TemplateResponse(request, 'pyBuchaktion/admin/order_order_selected_csv.html', context)
        elif request.POST.get('_ok'):
            pass  # return to list view
        elif not request.POST.get('_cancel'):
            context = dict(
                self.admin_site.each_context(request),
                title=_("Ordering: Are you sure?"),
                intro=_("The following orders will be marked as ordered. Are you sure?"),
                action='order_selected',
                queryset=queryset,
                opts=self.opts,
                action_checkbox_name=helpers.ACTION_CHECKBOX_NAME,
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

    fieldsets = [
        ("", {
            'fields': (('tuid_user', 'email'), ('library_id', 'language'))
        }),
    ]

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
                title=_("Send notification email"),
                intro=_("Write a custom notification here, which will be sent to all selected students"),
                action='sendmail',
                queryset=queryset,
                opts=self.opts,
                action_checkbox_name=helpers.ACTION_CHECKBOX_NAME,
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

    fieldsets = [
        ("", {
            'fields': (('semester',), ('start_date', 'end_date'), ('allowed_orders', 'spendings'))
        }),
    ]


@register(Semester)
class SemesterAdmin(ModelAdmin):
    """
        The admin for a semester.
    """

    fieldsets = [
        ("", {
            'fields': (('season', 'year'), ('budget',))
        }),
    ]

    # radio_fields = {"season": admin.VERTICAL}
    pass


SEMESTER_REGEX = re.compile("(W|S)(\d*)")


class SemesterWidget(Widget):
    def clean(self, value, row=None, *args, **kwargs):
        match = SEMESTER_REGEX.match(value)
        get_args = {'season': match.groups()[0], 'year': match.groups()[1]}
        return Semester.objects.get(**get_args)

    def render(self, value, obj=None):
        return "{0}{1}".format(value.season, value.year)


class TUCaNLiteratureWidget(ManyToManyWidget):
    def __init__(self):
        super().__init__(Book, separator=', ', field='isbn_13')


class TUCaNLiteratureField(Field):
    def __init__(self):
        super().__init__(column_name='books', attribute='literature', widget=TUCaNLiteratureWidget())

    def save(self, obj, data):
        ids = []
        for book in self.clean(data):
            try:
                literature_info = Literature.objects.get(book=book, module=obj)
                if not literature_info.in_tucan:
                    literature_info.update(in_tucan=True)
            except Literature.DoesNotExist:
                literature_info = Literature.objects.create(
                    book=book, module=module, source=Literature.TUCAN, in_tucan=True
                )
            ids.append(literature_info.pk)
        obj.refresh_from_db(fields=['literature', ])

        literature = Literature.objects.filter(module=obj).exclude(pk__in=ids)
        literature.filter(source=Literature.TUCAN).delete()
        literature.filter(in_tucan=True).update(in_tucan=False)

    def get_value(self, obj):
        return Book.objects.filter(
            literature_info__module=obj,
            literature_info__in_tucan=True,
        )


class ModuleResource(ForeignKeyImportResourceMixin, ModelResource):
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset.prefetch_related(Prefetch('literature'))
        return queryset

    books = TUCaNLiteratureField()
    category = Field(
        column_name='category',
        attribute='category',
        widget=ForeignKeyWidget(
            ModuleCategory,
            field='name_de',
        ),
    )

    last_offered = Field(
        column_name='last_offered',
        attribute='last_offered',
        widget=SemesterWidget()
    )

    class Meta:
        model = Module
        import_id_fields = (
            'module_id',
        )
        fields = import_id_fields + (
            'name_de',
            'name_en',
            'category',
            'last_offered',
            'books',
        )


@register(Module)
class ModuleAdmin(ImportExportMixin, ModelAdmin):
    """
        The admin for a module displays the name and module id.
    """

    resource_class = ModuleResource
    import_template_name = 'pyBuchaktion/admin/import.html'

    list_display = (
        'name_de_short',
        'name_en_short',
        'module_id',
        'category',
    )

    search_fields = [
        'name_de',
        'name_en',
        'module_id',
    ]

    list_filter = (
        'category',
    )

    fieldsets = [
        ("", {
            'fields': (('name_de', 'name_en'), ('module_id', 'category'), ('last_offered'))
        }),
    ]

    def name_de_short(self, obj):
        return Truncator(obj.name_de).chars(30)

    name_de_short.short_description = _("german name")
    name_de_short.admin_order_field = 'name_de'

    def name_en_short(self, obj):
        return Truncator(obj.name_en).chars(30)

    name_en_short.short_description = _("english name")
    name_en_short.admin_order_field = 'name_en'


@register(Literature)
class LiteratureAdmin(ModelAdmin):
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related(Prefetch('book'))
        queryset = queryset.prefetch_related(Prefetch('module'))
        return queryset

    list_display = (
        'title',
        'module_name',
        'source',
    )

    list_filter = (
        'source',
    )

    fieldsets = [
        ("", {
            'fields': (('module',), ('book',), ('source', 'in_tucan', 'active'))
        }),
    ]

    def title(self, obj):
        return Truncator(obj.book.title).chars(50)

    title.short_description = _("title")

    def module_name(self, obj):
        return Truncator(obj.module.name).chars(50)

    module_name.short_description = _("module")


class ModuleCategoryResource(ModelResource):
    class Meta:
        model = ModuleCategory
        import_id_fields = (
            'name_de',
        )
        fields = import_id_fields


@register(ModuleCategory)
class ModuleCategoryAdmin(ImportExportMixin, ModelAdmin):
    resource_class = ModuleCategoryResource

    list_display = (
        'id',
        'name_de',
        'name_en',
        'visible',
    )

    list_display_links = (
        'name_de',
    )

    fieldsets = (
        (_('Names'), {
            'fields': (('name_de', 'name_en'),)
        }),
        (_('Settings'), {
            'fields': (('visible',),)
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

    fieldsets = (
        ("", {
            'fields': (('key'), ('text_de', 'text_en'))
        }),
    )

    def trunc_de(self, obj):
        return Truncator(obj.text_de).chars(60)

    trunc_de.short_description = _("german text")

    def trunc_en(self, obj):
        return Truncator(obj.text_en).chars(60)

    trunc_en.short_description = _("english text")
