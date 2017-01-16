from django.contrib import admin

from . import models

@admin.register(models.Book)
class BookAdmin(admin.ModelAdmin):
	list_display = ('title', 'author', 'isbn_13')
	list_filter = ('state', 'author')

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = ('book_title', 'student', 'timeframe')
	list_filter = ('status', 'order_timeframe')
	
	def book_title(self, order):
		return order.book.title

	def timeframe(self, order):
		return order.order_timeframe.end_date

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
