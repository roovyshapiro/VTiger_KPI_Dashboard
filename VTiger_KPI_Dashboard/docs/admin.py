from django.contrib import admin
from .models import Docs

class Docs_admin(admin.ModelAdmin):
    readonly_fields = ('date_created','date_modified')

admin.site.register(Docs, Docs_admin)