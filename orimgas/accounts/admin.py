from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models

class UserAdmin(admin.ModelAdmin):
    list_display = ('email',)
    search_fields = ()

admin.site.register(models.User, UserAdmin)

