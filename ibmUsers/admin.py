from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from ibmUsers.models import User , Student , Teacher
from ibmUsers.forms import UserCreation , UserChange

class CustomUserAdmin(UserAdmin):
    add_form = UserCreation
    form = UserChange

    list_display = ('email' , 'first_name' , 'last_name', 'phone_number', 'is_teacher' , 'is_school_admin')
    list_filter = ('phone_number',)
    fieldsets = ((None,{'fields': ('email',) }),
                 ('Personal Info',{'fields':('first_name' , 'last_name' , 'phone_number')}),
                 ('Status', {'fields':('is_school_admin', 'is_teacher')}))

    add_fieldsets = ((None , {'classes':('wide',),
                              'fields':('email', 'first_name',  'last_name',  'password1', 'password2', 'phone_number', 'is_teacher',
                                        'is_school_admin', )},
                      ),)

    ordering = ('email',)


admin.site.register(User, CustomUserAdmin)
admin.site.register(Teacher)
admin.site.register(Student)
