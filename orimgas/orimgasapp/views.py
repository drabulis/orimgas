from typing import Any
from django.shortcuts import render
from django.contrib.auth.mixins import  LoginRequiredMixin
from django.db.models.query import QuerySet, Q
from django.http import HttpResponse
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django.http import FileResponse
from . import models, forms
from django.core.exceptions import PermissionDenied


class UserMeniuView(LoginRequiredMixin, generic.ListView):
    model = models.User
    template_name = 'main/menu.html'
    


class UserDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.User
    template_name = 'main/user_detail.html'
    fields = ['photo', 'first_name', 'last_name', 'email', 'position', 'instructions']


class AddUserView(LoginRequiredMixin, generic.CreateView):
    model = models.User
    form_class = forms.AddUserForm
    template_name = 'main/user_add.html'
    success_url = reverse_lazy('my_company_users')

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_supervisor:
            raise PermissionDenied("Tau čia negalima!")
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.user = self.request.user
        form.fields['position'].queryset = models.Position.objects.filter(company=self.request.user.company)
        form.fields['instructions'].queryset = models.Instruction.objects.filter(company=self.request.user.company)
        return form

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['company'] = self.request.user.company
        return context
    
    def form_valid(self, form):
        form.instance.company = self.request.user.company
        return super().form_valid(form)



class UserInstructionSignView(LoginRequiredMixin, generic.ListView):
    model = models.UserInstructionSign
    template_name = 'main/user_instructions.html'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset
    

class UserInstructionSignUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.UserInstructionSign
    form_class = forms.UserInstructionSignForm
    template_name = 'main/user_instruction_detail.html'

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['instruction'] = self.object.instruction
        context['status'] = 1
        context['date_signed'] = datetime.now()
        context['next_sign'] = datetime.now() + timedelta(int(self.object.instruction.periodiskumas))
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.status = 1
        form.instance.date_signed = datetime.now()
        form.instance.next_sign = datetime.now() + timedelta(int(self.object.instruction.periodiskumas))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('user_instructions')


def serve_pdf(request, instruction_id):
    instruction = get_object_or_404(models.Instruction, id=instruction_id)
    response = FileResponse(instruction.pdf, content_type='application/pdf')
    return response


class UserEditView(LoginRequiredMixin, generic.UpdateView):
    model = models.User
    template_name = 'main/user_edit.html'
    fields = ['email', 'first_name', 'last_name', 'password']


class MyCompanyUsersView(LoginRequiredMixin, generic.ListView):
    model = models.User
    template_name = 'main/my_company_users.html'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_supervisor:
            raise PermissionDenied("You do not have permission to access this view.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["search"] = True
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('query')
        company = self.request.user.company
        queryset = queryset.filter(company=company)
        if query:
            queryset = queryset.filter(
                Q(position__name__icontains=query)
                | Q(email__icontains=query)
                | Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
            )
        print("Queryset:", queryset)  
        return queryset


class SupervisorEditUserView(LoginRequiredMixin, generic.UpdateView):
    model = models.User
    form_class = forms.SupervisorEditUserForm
    template_name = 'main/supervisor_edit_user.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.user = self.request.user
        form.fields['position'].queryset = models.Position.objects.filter(company=self.request.user.company)
        form.fields['instructions'].queryset = models.Instruction.objects.filter(company=self.request.user.company)
        return form

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_supervisor:
            raise PermissionDenied("You do not have permission to access this view.")
        user_to_edit = self.get_object()
        if self.request.user.company != user_to_edit.company:
            raise PermissionDenied("You do not have permission to edit users from a different company.")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return models.User.objects.filter(company=self.request.user.company)

    def get_success_url(self):
        return reverse_lazy('my_company_users')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.save()
        instructions = form.cleaned_data.get('instructions')
        existing_signs = models.UserInstructionSign.objects.filter(user=user)

        for instruction in instructions:
            existing_sign = existing_signs.filter(instruction=instruction).first()
            if existing_sign:
                existing_sign.save()
            else:
                models.UserInstructionSign.objects.create(
                    user=user,
                    instruction=instruction,
                 )

        return super().form_valid(form)