from django import forms
from . import models
from accounts.models import MED_PATIKROS_PERIODAS

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
        widget=forms.SelectMultiple(attrs={'required': 'true'}),
        required=False
    )
    priesgaisrines = forms.ModelMultipleChoiceField(
        label="Priesgiasrinės instrukcijos",
        queryset=models.PriesgiasrinesInstrukcijos.objects.none(),
        widget=forms.SelectMultiple(attrs={'required': 'true'}),
        required=False
    )
    mokymai = forms.ModelMultipleChoiceField(
        label="Mokymai",
        queryset=models.Mokymai.objects.none(),
        widget=forms.SelectMultiple(attrs={'required': 'true'}),
        required=False
    )
    kiti_dokumentai = forms.ModelMultipleChoiceField(
        label="Kiti dokumentai",
        queryset=models.KitiDokumentai.objects.none(),
        widget=forms.SelectMultiple(attrs={'required': 'true'}),
        required=False
    )
    med_patikros_data = forms.DateField(
        label="Medžių patikros data",
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'yyyy-mm-dd'})
    )
    med_patikros_periodas = forms.ChoiceField(
        label=("Medicininės patikros periodas"),
        choices=MED_PATIKROS_PERIODAS,
        required=True,
        widget=forms.Select(attrs={'required': 'true'})
    )

    class Meta:
        model = models.User
        fields = ['first_name', 'last_name', 'email', 'date_of_birth', 'position', 'instructions', 'priesgaisrines', 'mokymai', 'kiti_dokumentai', 'med_patikros_data', 'med_patikros_periodas',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['position'].queryset = models.Position.objects.none()
        self.fields['instructions'].queryset = models.Instruction.objects.none()
        self.fields['priesgaisrines'].queryset = models.PriesgiasrinesInstrukcijos.objects.none()
        self.fields['mokymai'].queryset = models.Mokymai.objects.none()
        self.fields['kiti_dokumentai'].queryset = models.KitiDokumentai.objects.none()

    def save(self, commit=True):
        user = super().save(commit)
        user.set_password(self.cleaned_data["password"])
        
        user.save()

        instructions = self.cleaned_data.get('instructions', [])
        priesgaisrines = self.cleaned_data.get('priesgaisrines', [])
        mokymai = self.cleaned_data.get('mokymai', [])
        kiti_dokumentai = self.cleaned_data.get('kiti_dokumentai', [])

        for instruction in priesgaisrines:
            models.PriesgaisriniuPasirasymas.objects.create(user=user, instruction=instruction, status=0)
        for instruction in mokymai:
            models.MokymuPasirasymas.objects.create(user=user, instruction=instruction, status=0)
        for instruction in kiti_dokumentai:
            models.KituDocPasirasymas.objects.create(user=user, instruction=instruction, status=0)
        for instruction in instructions:
            models.UserInstructionSign.objects.create(user=user, instruction=instruction, status=0)

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
    position = forms.ModelChoiceField(
        label="Pareigos",
        queryset=models.Position.objects.none(),
        widget=forms.Select(attrs={'required': 'true'}),
        required=True
    )
    instructions = forms.ModelMultipleChoiceField(
        label="Instrukcijos",
        queryset=models.Instruction.objects.none(),
        widget=forms.SelectMultiple(attrs={'required': 'true'}),
        required=True
    )
    priesgaisrines = forms.ModelMultipleChoiceField(
        label="Priesgiasrinės instrukcijos",
        queryset=models.PriesgiasrinesInstrukcijos.objects.none(),
        widget=forms.SelectMultiple(attrs={'required': 'true'}),
        required=True
    )
    mokymai = forms.ModelMultipleChoiceField(
        label="Mokymai",
        queryset=models.Mokymai.objects.none(),
        widget=forms.SelectMultiple(attrs={'required': 'true'}),
        required=False
    )
    kiti_dokumentai = forms.ModelMultipleChoiceField(
        label="Kiti dokumentai",
        queryset=models.KitiDokumentai.objects.none(),
        widget=forms.SelectMultiple(attrs={'required': 'true'}),
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
    password = forms.CharField(
    label="Password",
    strip=False,
    required=False,
    widget=forms.PasswordInput(attrs={'placeholder': 'Palikti tuščia, jeigu slaptažodis nekeičiamas.'}),
    )
    is_active = forms.BooleanField(
        label="Yra aktyvus",
        required=False,
        initial=True
        )
    class Meta:
        model = models.User
        fields = ['first_name', 'last_name', 'email', 'position', 'instructions', 'priesgaisrines', 'mokymai', 'kiti_dokumentai', 'med_patikros_data','med_patikros_periodas', 'password','is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_password(self):
        # If the password is not provided, return the original password
        return self.cleaned_data.get('password') or self.instance.password
    
    
class UserInstructionSignForm(forms.ModelForm):
    class Meta:
        model = models.UserInstructionSign
        fields = ['status',]

    widgets = {
        'status' : forms.HiddenInput(),
    }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].widget = forms.HiddenInput()


class UserEditForm(forms.ModelForm):
    email = forms.EmailField(label="El. paštas")
    first_name = forms.CharField(label="Vardas")
    last_name = forms.CharField(label="Pavardė")
    password = forms.CharField(
        label="Slaptažodis",
        strip=False,
        required=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Palikti tuščia, jeigu slaptažodis nekeičiamas.'}),
    )

    class Meta:
        model = models.User
        fields = ['email', 'first_name', 'last_name', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['readonly'] = True
        self.fields['last_name'].widget.attrs['readonly'] = True

    def clean_password(self):
        # If the password is not provided, return the original password
        return self.cleaned_data.get('password') or self.instance.password
