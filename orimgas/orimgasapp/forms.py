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
        widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'yyyy-mm-dd'})
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

            # JavaScript to fetch the PDF and create an object URL dynamically
            script = f"""
            <script>
                document.addEventListener('DOMContentLoaded', function () {{
                    const pdfViewer = document.getElementById('pdfViewer');

                    // Fetch the PDF file from the server
                    fetch("{pdf_url}")
                        .then(response => {{
                            if (!response.ok) {{
                                throw new Error('Network response was not ok');
                            }}
                            return response.blob();
                        }})
                        .then(blob => {{
                            // Create an object URL for the PDF
                            const objectUrl = URL.createObjectURL(blob);
                            pdfViewer.src = objectUrl;

                            // Revoke the object URL after the PDF is loaded
                            pdfViewer.onload = function () {{
                                URL.revokeObjectURL(objectUrl);
                            }};
                        }})
                        .catch(error => {{
                            console.error('There was a problem with the fetch operation:', error);
                        }});
                }});
            </script>
            """

            # HTML for the iframe to display the PDF
            html = f"""
            {script}
            <iframe id="pdfViewer" width="90%" height="80%" type="application/pdf"></iframe>
            """
            return mark_safe(html)
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
        if hasattr(self.instance, 'AAP'):
            instruction = self.instance.AAP
        else:
            instruction = self.instance

        if instruction.pdf:
            pdf_url = instruction.pdf.url

            script = f"""
            <script>
                function displayPDF() {{
                    const pdfViewer = document.getElementById('pdfViewer');
                    const loadingIndicator = document.getElementById('pdf-loading');
                    const canUseBlob = !/iPhone|iPad|iPod/i.test(navigator.userAgent);
                    
                    // Modern browsers (non-iOS)
                    if (canUseBlob) {{
                        fetch("{pdf_url}")
                            .then(response => {{
                                if (!response.ok) throw new Error('Network error');
                                return response.blob();
                            }})
                            .then(blob => {{
                                const objectUrl = URL.createObjectURL(blob);
                                pdfViewer.onload = function() {{
                                    URL.revokeObjectURL(objectUrl);
                                    pdfViewer.style.opacity = 1;
                                    loadingIndicator.style.display = 'none';
                                }};
                                pdfViewer.src = objectUrl;
                            }})
                            .catch(error => {{
                                console.error('Fetch failed:', error);
                                // Fallback to direct URL
                                pdfViewer.src = "{pdf_url}";
                                loadingIndicator.style.display = 'none';
                                pdfViewer.style.opacity = 1;
                            }});
                    }} 
                    // iOS devices
                    else {{
                        pdfViewer.src = "{pdf_url}#toolbar=0&navpanes=0";
                        loadingIndicator.style.display = 'none';
                        pdfViewer.style.opacity = 1;
                    }}
                }}
                document.addEventListener('DOMContentLoaded', displayPDF);
            </script>
            """

            html = f"""
            <!-- Viewport meta tag for mobile scaling (#6) -->
            <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
            
            <!-- Loading state container (#2) -->
            <div style="position:relative; width:100%; height:80vh;">
                {script}
                <div id="pdf-loading" style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); text-align:center;">
                    <div style="border:4px solid #f3f3f3; border-top:4px solid #3498db; border-radius:50%; width:40px; height:40px; animation:spin 1s linear infinite; margin:0 auto;"></div>
                    <p style="margin-top:10px;">Loading document...</p>
                </div>
                
                <!-- Main PDF viewer -->
                <iframe id="pdfViewer" 
                        style="width:100%; height:100%; border:none; opacity:0; transition:opacity 0.3s;"
                        type="application/pdf"
                        allow="autoplay">
                    <p>Your browser doesn't support PDFs. <a href="{pdf_url}">Download instead</a></p>
                </iframe>
            </div>
            
            <!-- Simple spinner animation -->
            <style>
                @keyframes spin {{
                    0% {{ transform: rotate(0deg); }}
                    100% {{ transform: rotate(360deg); }}
                }}
            </style>
            """
            return mark_safe(html)
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

    class Meta:
        model = models.User
        fields = ['instructions', 'priesgaisrines','civiline_sauga', 'mokymai', 'kiti_dokumentai','kalba',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)