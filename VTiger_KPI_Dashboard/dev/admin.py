from django.contrib import admin
from .models import Redmine_issues

class Redmine_issues_admin(admin.ModelAdmin):
    readonly_fields = ('date_created','date_modified')

admin.site.register(Redmine_issues, Redmine_issues_admin)