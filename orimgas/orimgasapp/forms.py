from django.contrib.auth.forms import UserCreationForm
from django import forms
from . import models
import random
import string


class AddUserForm(UserCreationForm):
    class Meta:
        model = models.User
        fields = ['email', 'first_name', 'last_name', 'position', 'instructions', 'company']

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
    class Meta:
        model = models.User
        fields = ['email', 'first_name', 'last_name', 'position', 'instructions', 'company', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company'].widget = forms.HiddenInput()



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