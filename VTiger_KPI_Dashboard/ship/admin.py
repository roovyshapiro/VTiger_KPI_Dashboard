from django.contrib import admin
from .models import Products

class Products_admin(admin.ModelAdmin):
    readonly_fields = ('date_created','date_modified')

admin.site.register(Products, Products_admin)