from django.contrib import admin
from .models import Classes, Courses , Documents , GpaScale , Assignment , StudentsAssignment , Weights

# Register your models here.

admin.site.register(Classes)
admin.site.register(Courses)
admin.site.register(Documents)
admin.site.register(GpaScale)
admin.site.register(Assignment)
admin.site.register(StudentsAssignment)
admin.site.register(Weights)
