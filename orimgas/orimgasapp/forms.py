from django.contrib.auth.forms import UserCreationForm
from django.contrib.admin import widgets
from django import forms
from . import models
import random
import string


from django import forms
from django.contrib.auth.forms import UsernameField
from . import models

from django import forms
from . import models

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
        label="Instrukcijos",
        queryset=models.Instruction.objects.none(),
        widget=forms.SelectMultiple(attrs={'required': 'true'}),
        required=False
    )

    class Meta:
        model = models.User
        fields = ['first_name', 'last_name', 'email', 'date_of_birth', 'position', 'instructions']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['position'].queryset = models.Position.objects.none()
        self.fields['instructions'].queryset = models.Instruction.objects.none()

    def save(self, commit=True):
        user = super().save(commit)
        user.set_password(self.cleaned_data["password"])
        user.save()

        instructions = self.cleaned_data.get('instructions', [])
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
        required=False
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
        fields = ['first_name', 'last_name', 'email', 'position', 'instructions', 'password','is_active']

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
