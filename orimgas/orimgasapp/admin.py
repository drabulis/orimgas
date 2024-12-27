from django.contrib import admin
from rangefilter.filters import DateRangeFilter
from . import models
from .models import UserInstructionSign, Instruction
from django.utils.translation import gettext_lazy as _


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'company_id', 'manager')
    search_fields = ('name', 'company_id', 'manager')

class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'company')
    search_fields = ('name', 'company')
    list_filter = (
        'company',
    )

class InstructionAdmin(admin.ModelAdmin):
    list_display = ('name', 'company')
    search_fields = ('name', 'company')
    list_filter = (
        'company',
    )

class PriesrinesInstrukcijosAdmin(admin.ModelAdmin):
    list_display = ('pavadinimas', 'imone')
    search_fields = ('pavadinimas', 'imone')
    list_filter = (
        'imone',
    )


class CivilineSaugaAdmin(admin.ModelAdmin):
    list_display = ('pavadinimas', 'imone')
    search_fields = ('pavadinimas', 'imone')
    list_filter = (
        'imone',
    )

class MokymaiAdmin(admin.ModelAdmin):
    list_display = ('pavadinimas', 'imone')
    search_fields = ('pavadinimas', 'imone')
    list_filter = (
        'imone',
    )

class KitiDokumentaiAdmin(admin.ModelAdmin):
    list_display = ('pavadinimas', 'imone')
    search_fields = ('pavadinimas', 'imone')
    list_filter = (
        'imone',
    )

class AsmeninesApsaugosPriemonesAdmin(admin.ModelAdmin):
    list_display = ('pavadinimas', 'periodiskumas')
    search_fields = ('pavadinimas', 'periodiskumas')
    list_filter = (
        'periodiskumas',
        'pavadinimas',
    )

class UserInstructionSignAdmin(admin.ModelAdmin):
    list_display = ('user', 'instruction', 'status', 'date_signed', 'next_sign')
    search_fields = ('user__email','user__first_name','user__last_name', 'instruction__name', 'status')  # Assuming user has an email field
    list_filter = (
        'status',
        ('user__company', admin.RelatedOnlyFieldListFilter),
        ('date_signed', admin.DateFieldListFilter),  # Use built-in filter for date fields
    )


class KituDocPasirasymasAdmin(admin.ModelAdmin):
    list_display = ('user', 'instruction', 'status', 'date_signed', 'next_sign',)
    search_fields = ('user__email','user__first_name','user__last_name', 'instruction__pavadinimas', 'status', 'date_signed', 'next_sign',)
    list_filter = (
        'status',
        ('user__company', admin.RelatedOnlyFieldListFilter),
        ('date_signed', DateRangeFilter),
    )

class PriesgaisriniuPasirasymasAdmin(admin.ModelAdmin):
    list_display = ('user', 'instruction', 'status', 'date_signed', 'next_sign')
    search_fields = ('user__email','user__first_name','user__last_name', 'instruction__pavadinimas', 'status', 'date_signed', 'next_sign')
    list_filter = (
        'status',
        ('user__company', admin.RelatedOnlyFieldListFilter),
        ('date_signed', DateRangeFilter),
    )


class CivilineSaugaPasirasymasAdmin(admin.ModelAdmin):
    list_display = ('user', 'instruction', 'status', 'date_signed', 'next_sign')
    search_fields = ('user__email','user__first_name','user__last_name', 'instruction__pavadinimas', 'status', 'date_signed', 'next_sign')
    list_filter = (
        'status',
        ('user__company', admin.RelatedOnlyFieldListFilter),
        ('date_signed', DateRangeFilter),
    )

class MokymuPasirasymasAdmin(admin.ModelAdmin):
    list_display = ('user', 'instruction', 'status', 'date_signed', 'next_sign')
    search_fields = ('user__email','user__first_name','user__last_name', 'instruction__pavadinimas', 'status', 'date_signed', 'next_sign')
    list_filter = (
        'status',
        ('user__company', admin.RelatedOnlyFieldListFilter),
        ('date_signed', DateRangeFilter),
    )

class TestAdmin(admin.ModelAdmin):
    list_display = ('pavadinimas',)
    search_fields = ('pavadinimas',)

class TestoKlausimaiAdmin(admin.ModelAdmin):
    list_display = ('klausimas', 'testas')
    search_fields = ('klausimas', 'testas')
    list_filter = (
        'testas',
    )

class TestoAtsakymasAdmin(admin.ModelAdmin):
    list_display = ('atsakymas', 'klausimas')
    search_fields = ('atsakymas', 'klausimas')
    list_filter = (
        'klausimas',
    )

class AAPPasirasymasAdmin(admin.ModelAdmin):
    list_display = ('user', 'AAP', 'status', 'date_signed', 'next_sign')
    search_fields = ('user__email','AAP__pavadinimas', 'status', 'date_signed', 'next_sign')
    list_filter = (
        'status',
        ('user__company', admin.RelatedOnlyFieldListFilter),
        ('date_signed', DateRangeFilter),
)


admin.site.register(models.Company, CompanyAdmin)
admin.site.register(models.Position, PositionAdmin)
admin.site.register(models.Instruction, InstructionAdmin)
admin.site.register(models.PriesgiasrinesInstrukcijos, PriesrinesInstrukcijosAdmin)
admin.site.register(models.CivilineSauga, CivilineSaugaAdmin)
admin.site.register(models.Mokymai, MokymaiAdmin)
admin.site.register(models.KitiDokumentai, KitiDokumentaiAdmin)
admin.site.register(models.KituDocPasirasymas, KituDocPasirasymasAdmin)
admin.site.register(models.PriesgaisriniuPasirasymas, PriesgaisriniuPasirasymasAdmin)
admin.site.register(models.CivilineSaugaPasirasymas, CivilineSaugaPasirasymasAdmin)
admin.site.register(models.MokymuPasirasymas, MokymuPasirasymasAdmin)
admin.site.register(models.UserInstructionSign, UserInstructionSignAdmin)
admin.site.register(models.Testai, TestAdmin)
admin.site.register(models.TestoKlausimas, TestoKlausimaiAdmin)
admin.site.register(models.TestoAtsakymas, TestoAtsakymasAdmin)
admin.site.register(models.AAPPasirasymas, AAPPasirasymasAdmin)
admin.site.register(models.AsmeninesApsaugosPriemones, AsmeninesApsaugosPriemonesAdmin)

