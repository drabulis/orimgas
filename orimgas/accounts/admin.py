from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models

class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'company', 'position')
    search_fields = ('email', 'first_name', 'last_name', 'company', 'position')
    list_filter = (
        'company',
        'position',
    )

admin.site.register(models.User, UserAdmin)

