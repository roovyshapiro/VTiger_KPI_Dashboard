from django.contrib import admin
from .models import Sales_stats, Phone_calls

# Register your models here.
class Sales_statsAdmin(admin.ModelAdmin):
    readonly_fields = ('date_created','date_modified')
    
admin.site.register(Sales_stats, Sales_statsAdmin)
admin.site.register(Phone_calls)