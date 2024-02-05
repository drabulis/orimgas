from django.contrib import admin
from rangefilter.filters import DateRangeFilter
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
    list_filter = (
        'status',
        ('user__company', admin.RelatedOnlyFieldListFilter),
        ('date_signed', DateRangeFilter),  # Add the DateRangeFilter for the date range selection
    )


admin.site.register(models.Company, CompanyAdmin)
admin.site.register(models.Position, PositionAdmin)
admin.site.register(models.Instruction, InstructionAdmin)
admin.site.register(models.UserInstructionSign, UserInstructionSignAdmin)

