from typing import Any
from django.shortcuts import render
from django.contrib.auth.mixins import  LoginRequiredMixin
from django.db.models.query import QuerySet, Q
from django.views import generic
from . import models


class UserMeniuView(LoginRequiredMixin, generic.ListView):
    model = models.User
    template_name = 'main/menu.html'
    


class UserDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.User
    template_name = 'main/user_detail.html'
    fields = ['photo', 'first_name', 'last_name', 'email', 'position', 'instructions']


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

class MyCompanyUsersView(LoginRequiredMixin, generic.ListView):
    model = models.User
    template_name = 'main/my_company_users.html'
    paginate_by = 1

    
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["search"] = True
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('query')
        if query:
            queryset = queryset.filter(
                                         Q(position__name__icontains=query)
                                       | Q(email__icontains=query)
                                       | Q(first_name__icontains=query)
                                       | Q(last_name__icontains=query)
                                       )
        return queryset

        
    
