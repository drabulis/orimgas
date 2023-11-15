from django.contrib import admin
from . import models


class companyAdmin(admin.ModelAdmin):
    list_display = ('name', 'company_id', 'manager')
    search_fields = ('name', 'company_id', 'manager')



class positionAdmin(admin.ModelAdmin):
    list_display = ('name', 'company')
    search_fields = ('name', 'company')

class instructionAdmin(admin.ModelAdmin):
    list_display = ('name', 'company')
    search_fields = ('name', 'company')

class positionInstructionAdmin(admin.ModelAdmin):
    list_display = ('position', 'display_instructions')
    search_fields = ('position', 'display_instructions')



admin.site.register(models.Company, companyAdmin)
admin.site.register(models.Position, positionAdmin)
admin.site.register(models.Instruction, instructionAdmin)
admin.site.register(models.PositionInstruction, positionInstructionAdmin)

