from django.contrib import admin
from .models import Cases

class Cases_Admin(admin.ModelAdmin):
    readonly_fields = ('date_created','date_modified')

admin.site.register(Cases, Cases_Admin)