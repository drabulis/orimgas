from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
import uuid, base64
from datetime import datetime, timedelta

User = get_user_model()


class Company(models.Model):
    name = models.CharField(max_length=100)
    company_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    manager = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    

class Testai(models.Model):
    pavadinimas = models.CharField(max_length=100)

    def __str__(self):
        return self.pavadinimas


class TestoKlausimas(models.Model):
    klausimas = models.CharField(max_length=100)
    testas = models.ForeignKey(Testai,
                               verbose_name=_("test"),
                               on_delete=models.CASCADE,
                               related_name='klausimai'
                               )

    def __str__(self):
        return f"{self.testas} - {self.klausimas}"
    
class TestoAtsakymas(models.Model):
    atsakymas = models.CharField(max_length=100)
    klausimas = models.ForeignKey(TestoKlausimas,
                               verbose_name=_("answer"),
                               on_delete=models.CASCADE,
                               related_name='atsakymai'
                               )
    teisingas = models.BooleanField(default=False)

    def __str__(self):
        return self.atsakymas


class Mokymai(models.Model):
    imone = models.ForeignKey(Company,
                              verbose_name=_("company"),
                              on_delete=models.CASCADE,
                              related_name='mokymai'
                              )
    pavadinimas = models.CharField(max_length=100)
    periodiskumas = models.IntegerField(_("periodicity"),default=365, blank=True, null=True)
    pdf = models.FileField(upload_to='mokymai')
    testas = models.ForeignKey(Testai,
                               verbose_name=_("test"),
                               on_delete=models.CASCADE,
                               related_name='mokymai',
                               blank=True, null=True,
                               default=None
                               )
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.pavadinimas


INSTRUKTAVIMO_TIPAS = (
    (0, _("Įvadinis")),
    (1, _("Periodinis")),

)

class PriesgiasrinesInstrukcijos(models.Model):
    imone = models.ForeignKey(Company,
                              verbose_name=_("company"),
                              on_delete=models.CASCADE,
                              related_name='priesgiasrines_instrukcijos'
                              )
    pavadinimas = models.CharField(max_length=100)
    periodiskumas = models.IntegerField(_("periodicity"),default=365, blank=True, null=True)
    pdf = models.FileField(upload_to='priesgaisrines_instrukcijos')
    testas = models.ForeignKey(Testai,
                               verbose_name=_("test"),
                               on_delete=models.CASCADE,
                               related_name='priesgiasrines_instrukcijos',
                               blank=True, null=True,
                               default=None
                               )
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.pavadinimas


class KitiDokumentai(models.Model):
    imone = models.ForeignKey(Company,
                              verbose_name=_("company"),
                              on_delete=models.CASCADE,
                              related_name='kiti_dokumentai'
                              )
    pavadinimas = models.CharField(max_length=100)
    pdf = models.FileField(upload_to='kiti_dokumentai')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.pavadinimas
    
class CivilineSauga(models.Model):
    imone = models.ForeignKey(Company,
                              verbose_name=_("company"),
                              on_delete=models.CASCADE,
                              related_name='civiline_sauga'
                              )
    pavadinimas = models.CharField(max_length=100)
    periodiskumas = models.IntegerField(_("periodicity"),default=365, blank=True, null=True)
    pdf = models.FileField(upload_to='civiline_sauga')
    testas = models.ForeignKey(Testai,
                               verbose_name=_("test"),
                               on_delete=models.CASCADE,
                               related_name='civiline_sauga',
                               blank=True, null=True,
                               default=None
                               )
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.pavadinimas

class Instruction(models.Model):
    company = models.ForeignKey(Company, 
                                verbose_name=_("company"), 
                                on_delete=models.CASCADE,
                                related_name='instructions'
                                )
    name = models.CharField(max_length=100)
    periodiskumas = models.IntegerField(_("periodicity"),default=365, blank=True, null=True)
    pdf = models.FileField(upload_to='instructions')
    testas = models.ForeignKey(Testai,
                             verbose_name=_("test"),
                             on_delete=models.CASCADE,
                             related_name='instructions',
                             blank=True, null=True,
                             default=None
                             )
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return f"{self.name}"
    
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
        return f"{self.name}"
    
    def display_positions(self):
        return ', '.join([position.name for position in self.positions.all()])
    display_positions.short_description = _('positions')


SIGNATURE_STATUS = (
    (0, _("Nepasirašyta")),
    (1, _("Pasirašyta")),

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
    instruktavimo_tipas = models.PositiveSmallIntegerField(
        _("status"), choices=INSTRUKTAVIMO_TIPAS, default=0
    )
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    

    def display_instructions(self):
        return ', '.join([instruction.name for instruction in self.instruction.all()])
    display_instructions.short_description = _('instructions')

    def recreate_if_needed(self):
        # Check the instruction's instruktavimo_tipas field
        if self.instruktavimo_tipas == 0:
            # If instruktavimo_tipas is 0, change it to 1 and recreate the instance
            recreated_sign = UserInstructionSign.objects.create(
                user=self.user,
                instruction=self.instruction,
                status=0,
                date_signed=None,
                next_sign=None,
                instruktavimo_tipas=1,
            )
            return recreated_sign
        else:
            # If instruktavimo_tipas is already 1, do nothing
            recreated_sign = UserInstructionSign.objects.create(
            user=self.user,
            instruction=self.instruction,
            status=0,
            date_signed=None,
            next_sign=None,
        )
        # Recreate PriesgaisriniuPasirasymas instance
            return recreated_sign
    

class CivilineSaugaPasirasymas(models.Model):
    user = models.ForeignKey(User,
                            verbose_name=_("user"),
                            on_delete=models.CASCADE
                            )
    instruction = models.ForeignKey(CivilineSauga, 
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
    instruktavimo_tipas = models.PositiveSmallIntegerField(
        _("status"), choices=INSTRUKTAVIMO_TIPAS, default=0
    )
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    

    def display_instructions(self):
        return ', '.join([instruction.name for instruction in self.instruction.all()])
    display_instructions.short_description = _('instructions')

    def recreate_if_needed(self):
        # Check the instruction's instruktavimo_tipas field
        if self.instruktavimo_tipas == 0:
            # If instruktavimo_tipas is 0, change it to 1 and recreate the instance
            recreated_sign = CivilineSaugaPasirasymas.objects.create(
                user=self.user,
                instruction=self.instruction,
                status=0,
                date_signed=None,
                next_sign=None,
                instruktavimo_tipas=1,
            )
            return recreated_sign
        else:
            # If instruktavimo_tipas is already 1, do nothing
            recreated_sign = CivilineSaugaPasirasymas.objects.create(
            user=self.user,
            instruction=self.instruction,
            status=0,
            date_signed=None,
            next_sign=None,
        )
        # Recreate PriesgaisriniuPasirasymas instance
            return recreated_sign


class PriesgaisriniuPasirasymas(models.Model):
    user  = models.ForeignKey(User,
                            verbose_name=_("user"),
                            on_delete=models.CASCADE
                            )
    instruction = models.ForeignKey(PriesgiasrinesInstrukcijos,
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
    instruktavimo_tipas = models.PositiveSmallIntegerField(
        _("status"), choices=INSTRUKTAVIMO_TIPAS, default=0
    )
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def display_instructions(self):
        return ', '.join([instruction.name for instruction in self.instruction.all()])
    display_instructions.short_description = _('instructions')

    def recreate_if_needed(self):
        # Check the instruction's instruktavimo_tipas field
        if self.instruktavimo_tipas == 0:
            # If instruktavimo_tipas is 0, change it to 1 and recreate the instance
            recreated_sign = PriesgaisriniuPasirasymas.objects.create(
                user=self.user,
                instruction=self.instruction,
                status=0,
                date_signed=None,
                next_sign=None,
                instruktavimo_tipas=1,
            )
            return recreated_sign
        else:
            # If instruktavimo_tipas is already 1, do nothing
            recreated_sign = PriesgaisriniuPasirasymas.objects.create(
            user=self.user,
            instruction=self.instruction,
            status=0,
            date_signed=None,
            next_sign=None,
        )
        # Recreate PriesgaisriniuPasirasymas instance
            return recreated_sign
    

class MokymuPasirasymas(models.Model):
    user  = models.ForeignKey(User,
                            verbose_name=_("user"),
                            on_delete=models.CASCADE
                            )
    instruction = models.ForeignKey(Mokymai,
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
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    

    def display_instructions(self):
        return ', '.join([instruction.name for instruction in self.instruction.all()])
    display_instructions.short_description = _('instructions')

    def recreate_if_needed(self):
        # Recreate MokymuPasirasymas instance
        recreated_sign = MokymuPasirasymas.objects.create(
            user=self.user,
            instruction=self.instruction,
            status=0,
            date_signed=None,
            next_sign=None,
        )
        return recreated_sign
    

class KituDocPasirasymas(models.Model):
    user  = models.ForeignKey(User,
                            verbose_name=_("user"),
                            on_delete=models.CASCADE
                            )
    instruction = models.ForeignKey(KitiDokumentai,
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
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    

    def display_instructions(self):
        return ', '.join([instruction.pavadinimas for instruction in self.instruction.all()])
    display_instructions.short_description = _('instructions')

    def recreate_if_needed(self):
        # Recreate KituDocPasirasymas instance
        recreated_sign = KituDocPasirasymas.objects.create(
            user=self.user,
            instruction=self.instruction,
            status=0,
            date_signed=None,
            next_sign=None,
        )
        return recreated_sign