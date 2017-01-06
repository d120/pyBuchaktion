from django.contrib import admin

# Register your models here.

from . import models

admin.site.register(models.Book)
admin.site.register(models.Order)
admin.site.register(models.Student)
admin.site.register(models.OrderTimeframe)
admin.site.register(models.Semester)
admin.site.register(models.TucanModule)