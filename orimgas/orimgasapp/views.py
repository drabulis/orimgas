from django.shortcuts import render
from django.contrib.auth.mixins import  LoginRequiredMixin
from django.views import generic
from . import models


class UserMeniuView(LoginRequiredMixin, generic.ListView):
    model = models.User
    template_name = 'main/menu.html'
    


class UserDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.User
    template_name = 'main/user_detail.html'


class AddUserView(LoginRequiredMixin, generic.CreateView):
    model = models.User
    template_name = 'main/user_add.html'
    fields = ['email', 'first_name', 'last_name', 'position', 'instructions']


class UserInstructionsView(LoginRequiredMixin, generic.ListView):
    model = models.Instruction
    template_name = 'main/user_instructions.html'


class UserEditView(LoginRequiredMixin, generic.UpdateView):
    model = models.User
    template_name = 'main/user_edit.html'
    fields = ['email', 'first_name', 'last_name', 'password']
