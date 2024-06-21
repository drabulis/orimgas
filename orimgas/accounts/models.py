from typing import Any
from django.db import models
from django.urls import reverse
from datetime import timedelta
from django.utils.translation import gettext_lazy as _
import uuid
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager,AbstractBaseUser, PermissionsMixin

class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        
        email = self.normalize_email(email)
        password = make_password(password)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user
    
    def _create_superuser(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        
        email = self.normalize_email(email)
        password = make_password(password)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email=None, password=None, **extra_fields: Any) -> Any:
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)


    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_superuser(email, password, **extra_fields)
    
MED_PATIKROS_PERIODAS = (
    (12, _("12 Mėnesių")),
    (24, _("24 Mėnesių")),

)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(_("first name"), max_length=100)
    last_name = models.CharField(_("last name"), max_length=100)
    company = models.ForeignKey("orimgasapp.Company", 
                                verbose_name=_("company"), 
                                on_delete=models.CASCADE, 
                                blank=True, null=True, 
                                related_name="users")
    position = models.ForeignKey("orimgasapp.Position",
                                verbose_name=_("position"),
                                on_delete=models.CASCADE,
                                related_name="users",
                                blank=True, null=True,
                                default=None)
    instructions = models.ManyToManyField("orimgasapp.Instruction",
                                verbose_name=_("instructions"),
                                related_name="users",
                                blank=True,
                                default=None)
    priesgaisrines = models.ManyToManyField("orimgasapp.PriesgiasrinesInstrukcijos",
                                verbose_name=_("PriesgiasrinesInstrukcijos"),
                                related_name="users",
                                blank=True,
                                default=None)
    mokymai = models.ManyToManyField("orimgasapp.Mokymai",
                                verbose_name=_("mokymai"),
                                related_name="users",
                                blank=True,
                                default=None)
    kiti_dokumentai = models.ManyToManyField("orimgasapp.KitiDokumentai",
                                verbose_name=_("kiti dokumentai"),
                                related_name="users",
                                blank=True,
                                default=None)
    civiline_sauga = models.ManyToManyField("orimgasapp.CivilineSauga",
                                verbose_name=_("CivilineSauga"),
                                related_name="users",
                                blank=True,
                                default=None)
    date_of_birth = models.DateField(blank=True, null=True)
    med_patikros_data = models.DateField(blank=True, null=True)
    med_patikros_periodas = models.SmallIntegerField(
        _('med patikros periodas'), choices=MED_PATIKROS_PERIODAS, default=12)
    sekanti_med_patikros_data = models.DateField(blank=True, null=True)
    
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True, blank=True, null=True)
    
    is_supervisor = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        # Hash the password only if it's not already hashed
        if not self.password or not self.password.startswith(('pbkdf2_sha256$', 'bcrypt', 'argon2')):
            self.password = make_password(self.password)
        
        if not self.is_active:
            # Delete UserInstructionSign instances with status=0
            self.userinstructionsign_set.filter(status=0).delete()
            # Delete PriesgaisriniuPasirasymas instances with status=0
            self.priesgaisriniupasirasymas_set.filter(status=0).delete()
            # Delete MokymuPasirasymas instances with status=0
            self.mokymupasirasymas_set.filter(status=0).delete()
            # Delete KitiDocPasirasymas instances with status=0
            self.kitudocpasirasymas_set.filter(status=0).delete()


        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_short_name(self):
        return self.first_name or self.email.split('@')[0]