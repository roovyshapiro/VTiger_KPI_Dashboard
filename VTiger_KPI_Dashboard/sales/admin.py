from django.contrib import admin
from .models import Phone_call, Opportunities

class Phone_call_Admin(admin.ModelAdmin):
    readonly_fields = ('date_created','date_modified')

class Opportunities_Admin(admin.ModelAdmin):
    readonly_fields = ('date_created','date_modified')

admin.site.register(Phone_call, Phone_call_Admin)
admin.site.register(Opportunities, Opportunities_Admin)