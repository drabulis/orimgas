from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

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
    periodity = models.DateField(_("periodicity"), default=None, blank=True, null=True)
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


class PositionInstruction(models.Model):
    position = models.ForeignKey(Position, 
                                 verbose_name=_("position"), 
                                 on_delete=models.CASCADE,
                                 related_name='position_instruction'
                                 )
    instruction = models.ManyToManyField(Instruction,
                                        verbose_name=_("instruction"),
                                        related_name='position_instruction',
                                        )

    def display_instructions(self):
        return ', '.join([instruction.name for instruction in self.instruction.all()])
    display_instructions.short_description = _('instructions')

