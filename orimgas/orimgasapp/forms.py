from django.contrib.auth.forms import UserCreationForm
from django.contrib.admin import widgets
from django import forms
from . import models
import random
import string


class AddUserForm(UserCreationForm):
    date_of_birth = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'yyyy-mm-dd'}))
    class Meta:
        model = models.User
        fields = ['email', 'first_name', 'last_name','date_of_birth', 'position', 'instructions', 'company']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company'].widget = forms.HiddenInput()

    def save(self, commit=True):
        user = super().save(commit)
        instructions = self.cleaned_data.get('instructions', [])
        for instruction in instructions:
            models.UserInstructionSign.objects.create(user=user, instruction=instruction, status=0)
        return user


class SupervisorEditUserForm(forms.ModelForm):
    password = forms.CharField(
    label="Password",
    strip=False,
    required=False,
    widget=forms.PasswordInput(attrs={'placeholder': 'Palikti tuščia, jeigu slaptažodis nekeičiamas.'}),
    )
    class Meta:
        model = models.User
        fields = ['email', 'first_name', 'last_name', 'position', 'instructions', 'company', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company'].widget = forms.HiddenInput()

    def clean_password(self):
        # If the password is not provided, return the original password
        return self.cleaned_data.get('password', self.instance.password)




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
    password = forms.CharField(
    label="Password",
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
        return self.cleaned_data.get('password', self.instance.password)