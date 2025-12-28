from django import forms
from . import models
from accounts.models import MED_PATIKROS_PERIODAS, KALBA
from django.forms import ValidationError
from django.utils.safestring import mark_safe
import base64
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.core.mail import send_mail
from accounts.models import User


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
        widget=forms.DateInput(attrs={'class': 'datepicker', 'type': 'text', 'placeholder': 'yyyy-mm-dd', 'autocomplete': 'off'}, format='%Y-%m-%d'),
        input_formats=['%Y-%m-%d', '%d-%m-%Y', '%d.%m.%Y', '%d/%m/%Y']
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
        widget=forms.SelectMultiple(attrs={'size': '8', 'class': 'scrollable-select'}),
        required=True
    )
    civiline_sauga = forms.ModelMultipleChoiceField(
        label="Civiline sauga",
        queryset=models.CivilineSauga.objects.none(),
        widget=forms.SelectMultiple(attrs={'size': '8', 'class': 'scrollable-select'}),
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
        widget=forms.DateInput(attrs={'class': 'datepicker', 'type': 'text', 'placeholder': 'yyyy-mm-dd', 'autocomplete': 'off'}, format='%Y-%m-%d'),
        input_formats=['%Y-%m-%d', '%d-%m-%Y', '%d.%m.%Y', '%d/%m/%Y']
    )
    med_patikros_periodas = forms.ChoiceField(
        label=("Medicininės patikros periodas"),
        choices=MED_PATIKROS_PERIODAS,
        required=True,
        widget=forms.Select(attrs={'required': 'true'})
    )
    AsmeninesApsaugosPriemones = forms.ModelMultipleChoiceField(
        label="Asmenines apsaugos priemone",
        required=False,
        queryset=models.AsmeninesApsaugosPriemones.objects.none(),
        widget=forms.SelectMultiple(attrs={'size': '8', 'class': 'scrollable-select'}),
    )
    skyrius = forms.ModelChoiceField(
        label=("Skyrius"),
        queryset=models.Skyrius.objects.none(),
        required=False,
    )
    kalba = forms.ChoiceField(
        label=("Kalba"),
        choices=KALBA,
        required=True,
        widget=forms.Select(attrs={'required': 'true'})
    )

    class Meta:
        model = models.User
        fields = ['first_name', 'last_name', 'date_of_birth', 'email', 'position', 'instructions', 'priesgaisrines','civiline_sauga', 'mokymai', 'kiti_dokumentai', 'med_patikros_data', 'med_patikros_periodas', 'password', 'AsmeninesApsaugosPriemones','skyrius','kalba',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['position'].queryset = models.Position.objects.none()
        self.fields['instructions'].queryset = models.Instruction.objects.none()
        self.fields['priesgaisrines'].queryset = models.PriesgiasrinesInstrukcijos.objects.none()
        self.fields['mokymai'].queryset = models.Mokymai.objects.none()
        self.fields['kiti_dokumentai'].queryset = models.KitiDokumentai.objects.none()
        self.fields['civiline_sauga'].queryset = models.CivilineSauga.objects.none()
        self.fields['AsmeninesApsaugosPriemones'].queryset = models.AsmeninesApsaugosPriemones.objects.none()
        self.fields['skyrius'].queryset = models.Skyrius.objects.none()
        # self.fields['skyrius'].empty_label = "None" 
        
    def save(self, commit=True):

        user = super().save(commit)
        user.set_password(self.cleaned_data["password"])
        user.skyrius = self.cleaned_data["skyrius"]
        user.kalba = self.cleaned_data["kalba"]
        
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

        company = user.company.name
        company_id = user.company.id
        supervisor_list = User.objects.filter(is_supervisor=True, company=company_id)
        subject = f'Prisijungimas prie EIS. {company}'
        message = f"""
Gerbiamas(-a) {user.first_name},

Jūs prijungti prie elektroninės instruktavimo sistemos (EIS).
Kviečiame prisijungti prie jūsų profilio, susipažinti su instrukcijomis.
Prisijungti galite čia: https://orimgas.online
Informuojame, kad prisijungimo vardas yra jūsų elektroninis paštas.
Slaptažodis yra jūsų gimimo data.
Slaptažodžio formatas: Metai-Mėnuo-Diena (Skaičiais).
Iškilus klausimams kreipkitės į savo administratorių.\n"""
        for supervisor in supervisor_list:
            message += f'- {supervisor.first_name} {supervisor.last_name} - {supervisor.email}\n'
        message += f"""
Pagarbiai,
"Orimgas" komanda

Dear {user.first_name},

You have been connected to the electronic information system (EIS).
We invite you to log in to your profile and familiarize yourself with the instructions.
You can log in to your profile here: https://orimgas.online
Please note that your login username is your email address.
Your password is your date of birth.
Password format: Year-Month-Day (Numbers)
If you have any questions, please contact your supervisor.\n"""
        for supervisor in supervisor_list:
            message += f'- {supervisor.first_name} {supervisor.last_name} - {supervisor.email}\n'
        message += f"""

Best regards,
The „Orimgas“ Team


Уважаемый(-ая) {user.first_name},
      
Вы подключены к электронной  информационной системе (ЕИС), вас подключил администратор Варденис Паварденис. 
Приглашаем вас подключиться к своему профилю и ознакомиться с инструкциями.
Вы можете подключиться к профилю здесь: https://orimgas.online          
Обратите внимание, что логином является ваш адрес электронной почты. Пароль – год вашего рождения.
Формат пароля: Год-Месяц-День (цифры)
Если у вас возникнут вопросы, обратитесь к администратору:\n"""
        for supervisor in supervisor_list:
            message += f'- {supervisor.first_name} {supervisor.last_name} - {supervisor.email}\n'
        message += f"""
С уважением,
Команда „Orimgas“
"""
        send_mail(subject, message, 'info@orimgas.online', [user.email])
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
        widget=forms.DateInput(attrs={'class': 'datepicker', 'type': 'text', 'placeholder': 'yyyy-mm-dd', 'autocomplete': 'off'}, format='%Y-%m-%d'),
        input_formats=['%Y-%m-%d', '%d-%m-%Y', '%d.%m.%Y', '%d/%m/%Y']
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
        widget=forms.SelectMultiple(attrs={'size': '8', 'class': 'scrollable-select'}),
        required=True
    )
    civiline_sauga = forms.ModelMultipleChoiceField(
        label="Civiline sauga",
        queryset=models.CivilineSauga.objects.none(),
        widget=forms.SelectMultiple(attrs={'size': '8', 'class': 'scrollable-select'}),
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
        widget=forms.DateInput(attrs={'class': 'datepicker', 'type': 'text', 'placeholder': 'yyyy-mm-dd', 'autocomplete': 'off'}, format='%Y-%m-%d'),
        input_formats=['%Y-%m-%d', '%d-%m-%Y', '%d.%m.%Y', '%d/%m/%Y']
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
    AsmeninesApsaugosPriemones = forms.ModelMultipleChoiceField(
        label="Asmenines apsaugos priemones",
        queryset=models.AsmeninesApsaugosPriemones.objects.none(),
        widget=forms.SelectMultiple(attrs={'size': '8', 'class': 'scrollable-select'}),
        required=False 
    )
    skyrius = forms.ModelChoiceField(
        label=("Skyrius"),
        queryset=models.Skyrius.objects.none(),
        required=False,
    )
    kalba = forms.ChoiceField(
        label=("Kalba"),
        choices=KALBA,
        required=True,
        widget=forms.Select(attrs={'required': 'true'})
    )

    class Meta:
        model = models.User
        fields = ['first_name', 'last_name', 'date_of_birth', 'email', 'position', 'instructions', 'priesgaisrines','civiline_sauga', 'mokymai', 'kiti_dokumentai', 'med_patikros_data','med_patikros_periodas', 'password','is_active', 'AsmeninesApsaugosPriemones','skyrius','kalba',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Format date fields to display in YYYY-MM-DD format
        if self.instance and self.instance.pk:
            if self.instance.date_of_birth:
                self.initial['date_of_birth'] = self.instance.date_of_birth
            if self.instance.med_patikros_data:
                self.initial['med_patikros_data'] = self.instance.med_patikros_data


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
            # URL to fetch the PDF file
            pdf_url = instruction.pdf.url
            cache_buster = int(time.time())
            html = f"""
            <!-- PDF Display Container -->
            <div style="width:100%; height:80vh; position:relative;">
                <!-- Method 1: PDF.js Viewer -->
                <iframe src="{static('pdfjs/web/viewer.html')}?file={pdf_url}"
                        style="width:100%; height:100%; border:none;"
                        id="pdfjs-viewer">
                    Your browser doesn't support iframes
                </iframe>
                
                <!-- Method 2: Direct Link Fallback -->
                <div id="pdf-fallback" style="
                    position:absolute; 
                    top:50%; 
                    left:50%; 
                    transform:translate(-50%,-50%);
                    text-align:center;
                    display:none;
                ">
                    <p style="margin-bottom:20px;">PDF viewer unavailable</p>
                    <a href="{pdf_url}?t={cache_buster}" 
                    download
                    style="
                        padding:12px 24px;
                        background:#4285f4;
                        color:white;
                        text-decoration:none;
                        border-radius:4px;
                    ">
                    Download PDF
                    </a>
                </div>
            </div>

            <!-- Fallback Detection -->
            <script>
                document.getElementById('pdfjs-viewer').onerror = function() {{
                    this.style.display = 'none';
                    document.getElementById('pdf-fallback').style.display = 'block';
                }};
                setTimeout(function() {{
                    if (document.getElementById('pdfjs-viewer').clientHeight === 0) {{
                        document.getElementById('pdfjs-viewer').style.display = 'none';
                        document.getElementById('pdf-fallback').style.display = 'block';
                    }}
                }}, 3000);
            </script>
            """
        else:
            html = ''
        
        
        return mark_safe(html)

    class Meta:
        model = models.UserInstructionSign
        fields = ['status']
        widgets = {
            'status': forms.HiddenInput(),
        }


from django import forms
from django.utils.safestring import mark_safe
from django.templatetags.static import static
import time

class RenderPDFForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)

    def render_pdf(self):
        if not getattr(self, 'instance', None):
            return ''

        instruction = getattr(self.instance, 'AAP', self.instance)
        if not instruction or not instruction.pdf:
            return ''

        pdf_url = instruction.pdf.url
        cache_buster = int(time.time())

        html = f"""
        <!-- PDF Display Container -->
        <div style="width:100%; height:80vh; position:relative;">
            <!-- Method 1: PDF.js Viewer -->
            <iframe src="{static('pdfjs/web/viewer.html')}?file={pdf_url}"
                    style="width:100%; height:100%; border:none;"
                    id="pdfjs-viewer">
                Your browser doesn't support iframes
            </iframe>
            
            <!-- Method 2: Direct Link Fallback -->
            <div id="pdf-fallback" style="
                position:absolute; 
                top:50%; 
                left:50%; 
                transform:translate(-50%,-50%);
                text-align:center;
                display:none;
            ">
                <p style="margin-bottom:20px;">PDF viewer unavailable</p>
                <a href="{pdf_url}?t={cache_buster}" 
                   download
                   style="
                       padding:12px 24px;
                       background:#4285f4;
                       color:white;
                       text-decoration:none;
                       border-radius:4px;
                   ">
                   Download PDF
                </a>
            </div>
        </div>

        <!-- Fallback Detection -->
        <script>
            document.getElementById('pdfjs-viewer').onerror = function() {{
                this.style.display = 'none';
                document.getElementById('pdf-fallback').style.display = 'block';
            }};
            setTimeout(function() {{
                if (document.getElementById('pdfjs-viewer').clientHeight === 0) {{
                    document.getElementById('pdfjs-viewer').style.display = 'none';
                    document.getElementById('pdf-fallback').style.display = 'block';
                }}
            }}, 3000);
        </script>
        """
        return mark_safe(html)
    
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


class InstructionAddAllForm(forms.ModelForm):
    instructions = forms.ModelMultipleChoiceField(
        label="Darbų saugos instrukcijos",
        queryset=models.Instruction.objects.none(),
        widget=forms.SelectMultiple(attrs={'size': '8', 'class': 'scrollable-select'}),
        required=False
    )
    priesgaisrines = forms.ModelMultipleChoiceField(
        label="Priesgiasrinės instrukcijos",
        queryset=models.PriesgiasrinesInstrukcijos.objects.none(),
        widget=forms.SelectMultiple(attrs={'size': '8', 'class': 'scrollable-select'}),
        required=False
    )
    civiline_sauga = forms.ModelMultipleChoiceField(
        label="Civiline sauga",
        queryset=models.CivilineSauga.objects.none(),
        widget=forms.SelectMultiple(attrs={'size': '8', 'class': 'scrollable-select'}),
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
    skyrius = forms.ModelChoiceField(
        label=("Skyrius"),
        queryset=models.Skyrius.objects.none(),
        required=False,
    )
    position = forms.ModelChoiceField(
        label=("Skyrius"),
        queryset=models.Position.objects.none(),
        required=False,
    )

    class Meta:
        model = models.User
        fields = ['instructions', 'priesgaisrines','civiline_sauga', 'mokymai', 'kiti_dokumentai','kalba',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)