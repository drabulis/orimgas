from django.contrib import admin
from . import models


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'company_id', 'manager')
    search_fields = ('name', 'company_id', 'manager')



class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'company')
    search_fields = ('name', 'company')

class InstructionAdmin(admin.ModelAdmin):
    list_display = ('name', 'company')
    search_fields = ('name', 'company')

class UserInstructionSignAdmin(admin.ModelAdmin):
    list_display = ('user', 'instruction', 'status', 'date_signed', 'next_sign')
    search_fields = ('user', 'instruction', 'status', 'date_signed', 'next_sign')



admin.site.register(models.Company, CompanyAdmin)
admin.site.register(models.Position, PositionAdmin)
admin.site.register(models.Instruction, InstructionAdmin)
admin.site.register(models.UserInstructionSign, UserInstructionSignAdmin)

