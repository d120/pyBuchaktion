from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
#from import_export import resources
#from import_export.admin import ImportExportActionModelAdmin
from django.http import HttpResponse
import io
import csv

from . import models

@admin.register(models.Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn_13')
    list_filter = ('state',)

#class OrderResource(resources.ModelResource):

#    class Meta:
#        model = models.Order

@admin.register(models.Order)
#class OrderAdmin(ImportExportActionModelAdmin):
class OrderAdmin(admin.ModelAdmin):
    list_display = ('book_title', 'student', 'timeframe')
    list_filter = ('status', 'order_timeframe')
    actions = ["export"]

    def book_title(self, order):
        return order.book.title

    def timeframe(self, order):
        return order.order_timeframe.end_date

    def export(self, request, queryset):

        out_stream = io.StringIO()
        writer = csv.writer(out_stream, delimiter='|', quotechar="\"", quoting=csv.QUOTE_MINIMAL)
        for order in queryset:
            array = [
                "", # ULB-Nummer
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
    pass

@admin.register(models.OrderTimeframe)
class OrderTimeframeAdmin(admin.ModelAdmin):
    list_display = ('end_date', 'start_date', 'semester')

@admin.register(models.Semester)
class SemesterAdmin(admin.ModelAdmin):
    #radio_fields = {"season": admin.VERTICAL}
    pass

@admin.register(models.TucanModule)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'module_id')
