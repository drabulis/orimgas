from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from datetime import datetime

User = get_user_model()


class Company(models.Model):
    name = models.CharField(max_length=100)
    company_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    manager = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Instruction(models.Model):
    company = models.ForeignKey(Company, 
                                verbose_name=_("company"), 
                                on_delete=models.CASCADE,
                                related_name='instructions'
                                )
    name = models.CharField(max_length=100)
    periodiskumas = models.IntegerField(_("periodicity"),default=0, blank=True, null=True)
    pdf = models.FileField(upload_to='instructions')

    def __str__(self):
        return f"{self.company} {self.name}"
    
    def display_instuctions(self):
        return ', '.join([instruction.name for instruction in self.instructions.all()])
    display_instuctions.short_description = _('instructions')


class Position(models.Model):
    name = models.CharField(max_length=100)
    company = models.ForeignKey(Company,
                                verbose_name=_("company"), 
                                on_delete=models.CASCADE,
                                related_name='positions'
                                )

    def __str__(self):
        return f"{self.company} {self.name}"
    
    def display_positions(self):
        return ', '.join([position.name for position in self.positions.all()])
    display_positions.short_description = _('positions')


SIGNATURE_STATUS = (
    (0, _("not signed")),
    (1, _("signed")),

)

class UserInstructionSign(models.Model):
    user = models.ForeignKey(User,
                            verbose_name=_("user"),
                            on_delete=models.CASCADE
                            )
    instruction = models.ForeignKey(Instruction, 
                                    verbose_name=_("instruction"), 
                                    on_delete=models.CASCADE
                                    )
    status = models.PositiveSmallIntegerField(
        _("status"), choices=SIGNATURE_STATUS, default=0
    )
    date_signed = models.DateField(_("date signed"), 
                                   default=None, blank=True, null=True)
    next_sign = models.DateField(_("next sign"),
                                 default=None, blank=True, null=True)
    

    def display_instructions(self):
        return ', '.join([instruction.name for instruction in self.instruction.all()])
    display_instructions.short_description = _('instructions')

