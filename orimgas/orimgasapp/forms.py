from django import forms
from . import models
from accounts.models import MED_PATIKROS_PERIODAS
from django.forms import ValidationError
from django.utils.safestring import mark_safe
import base64
from django.utils.translation import gettext_lazy as _



class AddUserForm(forms.ModelForm):
    first_name = forms.CharField(
    label="Vardas",
    strip=False,
    required=True,
    widget=forms.TextInput(attrs={'placeholder': 'Vardas'}),
    )
    last_name = forms.CharField(
        label="Pavardė",
        strip=False,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Pavardė'}),
    )
    email = forms.EmailField(
        label="El. paštas",
    )
    password = forms.CharField(
        label="Slaptažodis",
        strip=False,
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Slaptažodis'}),
    )
    date_of_birth = forms.DateField(
        label="Gimimo data",
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'yyyy-mm-dd'}),
        input_formats=['%Y-%m-%d']
    )
    position = forms.ModelChoiceField(
        label="Pareigos",
        queryset=models.Position.objects.none(),
        widget=forms.Select(attrs={'required': 'true'}),
        required=True
    )
    instructions = forms.ModelMultipleChoiceField(
        label="Darbų saugos instrukcijos",
        queryset=models.Instruction.objects.none(),
        widget=forms.SelectMultiple(attrs={'size': '8', 'class': 'scrollable-select'}),
        required=True
    )
    priesgaisrines = forms.ModelMultipleChoiceField(
        label="Priesgiasrinės instrukcijos",
        queryset=models.PriesgiasrinesInstrukcijos.objects.none(),
        widget=forms.SelectMultiple(attrs={'class': 'scrollable-select'}),
        required=True
    )
    civiline_sauga = forms.ModelMultipleChoiceField(
        label="Civiline sauga",
        queryset=models.CivilineSauga.objects.none(),
        widget=forms.SelectMultiple(attrs={'class': 'scrollable-select'}),
        required=False
    )
    mokymai = forms.ModelMultipleChoiceField(
        label="Mokymai",
        queryset=models.Mokymai.objects.none(),
        widget=forms.SelectMultiple(attrs={'class': 'scrollable-select'}),
        required=False
    )
    kiti_dokumentai = forms.ModelMultipleChoiceField(
        label="Kiti dokumentai",
        queryset=models.KitiDokumentai.objects.none(),
        widget=forms.SelectMultiple(attrs={'class': 'scrollable-select'}),
        required=False
    )
    med_patikros_data = forms.DateField(
        label="Medicininės patikros data",
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'yyyy-mm-dd'})
    )
    med_patikros_periodas = forms.ChoiceField(
        label=("Medicininės patikros periodas"),
        choices=MED_PATIKROS_PERIODAS,
        required=True,
        widget=forms.Select(attrs={'required': 'true'})
    )
    AsmeninesApsaugosPriemones = forms.ModelChoiceField(
        label="Asmenines apsaugos priemone",
        queryset=models.AsmeninesApsaugosPriemones.objects.none(),
        widget=forms.SelectMultiple(attrs={'size': '8', 'class': 'scrollable-select'}),
    )
    class Meta:
        model = models.User
        fields = ['first_name', 'last_name', 'date_of_birth', 'email', 'position', 'instructions', 'priesgaisrines','civiline_sauga', 'mokymai', 'kiti_dokumentai', 'med_patikros_data', 'med_patikros_periodas', 'password', 'AsmeninesApsaugosPriemones',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['position'].queryset = models.Position.objects.none()
        self.fields['instructions'].queryset = models.Instruction.objects.none()
        self.fields['priesgaisrines'].queryset = models.PriesgiasrinesInstrukcijos.objects.none()
        self.fields['mokymai'].queryset = models.Mokymai.objects.none()
        self.fields['kiti_dokumentai'].queryset = models.KitiDokumentai.objects.none()
        self.fields['civiline_sauga'].queryset = models.CivilineSauga.objects.none()
        self.fields['AsmeninesApsaugosPriemones'].queryset = models.AsmeninesApsaugosPriemones.objects.none()

    def save(self, commit=True):

        user = super().save(commit)
        user.set_password(self.cleaned_data["password"])
        
        user.save()

        instructions = self.cleaned_data.get('instructions', [])
        priesgaisrines = self.cleaned_data.get('priesgaisrines', [])
        civiline_sauga = self.cleaned_data.get('civiline_sauga', [])
        mokymai = self.cleaned_data.get('mokymai', [])
        kiti_dokumentai = self.cleaned_data.get('kiti_dokumentai', [])
        asmenines_apsaugos_priemones = self.cleaned_data.get('AsmeninesApsaugosPriemones', [])

        for instruction in priesgaisrines:
            models.PriesgaisriniuPasirasymas.objects.create(user=user, instruction=instruction, status=0,)
        for instruction in mokymai:
            models.MokymuPasirasymas.objects.create(user=user, instruction=instruction, status=0)
        for instruction in kiti_dokumentai:
            models.KituDocPasirasymas.objects.create(user=user, instruction=instruction, status=0)
        for instruction in instructions:
            models.UserInstructionSign.objects.create(user=user, instruction=instruction, status=0)
        for instruction in civiline_sauga:
            models.CivilineSaugaPasirasymas.objects.create(user=user, instruction=instruction, status=0)
        for instruction in asmenines_apsaugos_priemones:
            models.AAPPasirasymas.objects.create(user=user, AAP=instruction, status=0)
        return user


class SupervisorEditUserForm(forms.ModelForm):
    first_name = forms.CharField(
    label="Vardas",
    strip=False,
    required=True,
    widget=forms.TextInput(attrs={'placeholder': 'Vardas'}),
    )
    last_name = forms.CharField(
        label="Pavardė",
        strip=False,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Pavardė'}),
    )
    email = forms.EmailField(
        label="El. paštas",
    )
    password = forms.CharField(
        label="Slaptažodis",
        strip=False,
        required=False,
        widget=forms.PasswordInput(attrs={'placeholder': _('Nekeičiant, palikti tuščia.')}),
    )
    date_of_birth = forms.DateField(
        label="Gimimo data",
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'yyyy-mm-dd'})
    )
    position = forms.ModelChoiceField(
        label="Pareigos",
        queryset=models.Position.objects.none(),
        widget=forms.Select(attrs={'required': 'true'}),
        required=True
    )
    instructions = forms.ModelMultipleChoiceField(
        label="Darbų saugos instrukcijos",
        queryset=models.Instruction.objects.none(),
        widget=forms.SelectMultiple(attrs={'size': '8', 'class': 'scrollable-select'}),
        required=True
    )
    priesgaisrines = forms.ModelMultipleChoiceField(
        label="Priesgiasrinės instrukcijos",
        queryset=models.PriesgiasrinesInstrukcijos.objects.none(),
        widget=forms.SelectMultiple(attrs={'class': 'scrollable-select'}),
        required=True
    )
    civiline_sauga = forms.ModelMultipleChoiceField(
        label="Civiline sauga",
        queryset=models.CivilineSauga.objects.none(),
        widget=forms.SelectMultiple(attrs={'class': 'scrollable-select'}),
        required=False
    )
    mokymai = forms.ModelMultipleChoiceField(
        label="Mokymai",
        queryset=models.Mokymai.objects.none(),
        widget=forms.SelectMultiple(attrs={'class': 'scrollable-select'}),
        required=False
    )
    kiti_dokumentai = forms.ModelMultipleChoiceField(
        label="Kiti dokumentai",
        queryset=models.KitiDokumentai.objects.none(),
        widget=forms.SelectMultiple(attrs={'class': 'scrollable-select'}),
        required=False
    )
    med_patikros_data = forms.DateField(
        label="Medicininės patikros data",
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'yyyy-mm-dd'})
    )
    med_patikros_periodas = forms.ChoiceField(
        label=("Medicininės patikros periodas"),
        choices=MED_PATIKROS_PERIODAS,
        required=True,
        widget=forms.Select(attrs={'required': 'true'})
    )
    is_active = forms.BooleanField(
        label="Yra aktyvus",
        required=False,
        initial=True
        )
    class Meta:
        model = models.User
        fields = ['first_name', 'last_name', 'date_of_birth', 'email', 'position', 'instructions', 'priesgaisrines','civiline_sauga', 'mokymai', 'kiti_dokumentai', 'med_patikros_data','med_patikros_periodas', 'password','is_active', 'AsmeninesApsaugosPriemones']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_password(self):
        # If the password is not provided, return the original password
        return self.cleaned_data.get('password') or self.instance.password
    
    




from django.utils.safestring import mark_safe

class UserInstructionSignForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self.instance, 'AAP'):
            instruction = self.instance.AAP
        else:
            instruction = self.instance.instruction
        test = instruction.testas if hasattr(instruction, 'testas') else None
        if test:
            self.test_data = {}
            for klausimas in test.klausimai.all():
                atsakymai = klausimas.atsakymai.all()
                choices = [(atsakymas.id, atsakymas.atsakymas) for atsakymas in atsakymai]
                self.fields[f'question_{klausimas.id}'] = forms.ChoiceField(
                    choices=choices,
                    widget=forms.RadioSelect(),
                    label=klausimas.klausimas
                )
                self.test_data[klausimas.id] = [atsakymas.id for atsakymas in atsakymai if atsakymas.teisingas]


    def clean(self):
        cleaned_data = super().clean()
        if hasattr(self, 'test_data'):
            for field_name, field_value in cleaned_data.items():
                if field_name.startswith('question_'):
                    klausimas_id = int(field_name.split('_')[1])
                    if field_value:
                        if int(field_value) not in self.test_data[klausimas_id]:
                            raise ValidationError(_("Selected test answer is incorrect."))
                    else:
                        raise ValidationError(_("All questions must be answered."))
        return cleaned_data

    def render_pdf(self):
        if hasattr(self.instance, 'AAP'):
            instruction = self.instance.AAP
        else:
            instruction = self.instance.instruction
        if instruction.pdf:
            with open(instruction.pdf.path, 'rb') as f:
                pdf_content_base64 = base64.b64encode(f.read()).decode('utf-8')
                embed_attributes = {
                    'src': f'data:application/pdf;base64,{pdf_content_base64}',
                    'type': 'application/pdf',
                    'width': '100%',
                    'height': '600px',
                    'zoom': '83',  # Set default zoom level to 83%
                    'pluginspage': 'http://www.adobe.com/products/acrobat/readstep2.html',
                    'menu': 'false',  # Disable the upper menu
                    'contextmenu': 'false',  # Disable the right-click context menu
                    'download': 'false',  # Disable the download option
                    'readonly': 'true',  # Make the PDF readonly
                }
                embed_tag = '<embed ' + ' '.join([f'{attr}="{value}"' for attr, value in embed_attributes.items()]) + '>'
                return mark_safe(embed_tag)
        else:
            return ''

    class Meta:
        model = models.UserInstructionSign
        fields = ['status']
        widgets = {
            'status': forms.HiddenInput(),
        }


class RenderPDFForm(forms.Form):
    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        super(RenderPDFForm, self).__init__(*args, **kwargs)
        self.instance = instance

    def render_pdf(self):
        if self.instance:
            instruction = self.instance
            if instruction.pdf:
                with open(instruction.pdf.path, 'rb') as f:
                    pdf_content_base64 = base64.b64encode(f.read()).decode('utf-8')
                    embed_attributes = {
                        'src': f'data:application/pdf;base64,{pdf_content_base64}',
                        'type': 'application/pdf',
                        'width': '550px',
                        'height': '600px',
                        'zoom': '83',  # Set default zoom level to 83%
                        'pluginspage': 'http://www.adobe.com/products/acrobat/readstep2.html',
                        'menu': 'false',  # Disable the upper menu
                        'contextmenu': 'false',  # Disable the right-click context menu
                        'download': 'false',  # Disable the download option
                        'readonly': 'true',  # Make the PDF readonly
                    }
                    embed_tag = '<embed ' + ' '.join([f'{attr}="{value}"' for attr, value in embed_attributes.items()]) + '>'
                    return mark_safe(embed_tag)
            else:
                return ''
        else:
            return ''


class UserEditForm(forms.ModelForm):
    email = forms.EmailField(label=_("El. paštas"))
    first_name = forms.CharField(label=_("Vardas"))
    last_name = forms.CharField(label=_("Pavardė"))
    password = forms.CharField(
        label=_("Slaptažodis"),
        strip=False,
        required=False,
        widget=forms.PasswordInput(attrs={'placeholder': _('Palikti tuščia, jeigu slaptažodis nekeičiamas.')}),
    )

    class Meta:
        model = models.User
        fields = ['email', 'first_name', 'last_name', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['readonly'] = True
        self.fields['last_name'].widget.attrs['readonly'] = True
        self.fields['email'].widget.attrs['readonly'] = True

    def clean_password(self):
        # If the password is not provided, return the original password
        return self.cleaned_data.get('password') or self.instance.password
