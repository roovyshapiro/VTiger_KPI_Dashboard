from django.contrib import admin
from .models import Sales_stats

# Register your models here.
class Sales_statsAdmin(admin.ModelAdmin):
    readonly_fields = ('date_created',)
    
admin.site.register(Sales_stats, Sales_statsAdmin)
