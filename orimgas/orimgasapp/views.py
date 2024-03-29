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
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.conf import settings



class UserMeniuView(LoginRequiredMixin, generic.ListView):
    model = models.User
    template_name = 'main/menu.html'
    


class UserDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.User
    template_name = 'main/user_detail.html'
    fields = ['first_name', 'last_name', 'date_of_birth', 'email', 'position', 'instructions', 'priesgaisrines', 'mokymai', 'kiti_dokumentai', 'med_patikros_data','med_patikros_periodas',]

    def get_object(self, queryset=None):
        uuid = self.kwargs.get('uuid')
        return get_object_or_404(models.User, uuid=uuid)


class AddUserView(LoginRequiredMixin, generic.CreateView):
    model = models.User
    form_class = forms.AddUserForm
    template_name = 'main/user_add.html'
    success_url = reverse_lazy('my_company_users')

    def dispatch(self, request, *args, **kwargs):
        print("You got this far")
        if not self.request.user.is_supervisor:
            raise PermissionDenied("Tau čia negalima!")
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        print("You got this far get_form")
        form.fields['position'].queryset = models.Position.objects.filter(company=self.request.user.company)
        form.fields['instructions'].queryset = models.Instruction.objects.filter(company=self.request.user.company)
        form.fields['priesgaisrines'].queryset = models.PriesgiasrinesInstrukcijos.objects.filter(imone=self.request.user.company)
        form.fields['mokymai'].queryset = models.Mokymai.objects.filter(imone=self.request.user.company)
        form.fields['kiti_dokumentai'].queryset = models.KitiDokumentai.objects.filter(imone=self.request.user.company)
        form.fields['civiline_sauga'].queryset = models.CivilineSauga.objects.filter(imone=self.request.user.company)
        return form

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['company'] = self.request.user.company
        return context
    
    def form_valid(self, form):
        print("You got this far")
        form.instance.company = self.request.user.company
        med_patikros_data = form.cleaned_data.get('med_patikros_data')
        med_patikros_periodas = form.cleaned_data.get('med_patikros_periodas')


        if med_patikros_data and med_patikros_periodas:
            if isinstance(med_patikros_periodas, str):
                med_patikros_periodas = int(med_patikros_periodas)
            timedelta_periodas = timedelta(days=med_patikros_periodas / 12 * 365)
            form.instance.sekanti_med_patikros_data = med_patikros_data + timedelta_periodas

        return super().form_valid(form)


class UserInstructionSignView(LoginRequiredMixin, generic.ListView):
    model = models.UserInstructionSign
    template_name = 'main/user_instructions.html'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user, status=0)
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['priesrines_instrukcijos'] = models.PriesgaisriniuPasirasymas.objects.filter(user=self.request.user, status=0)
        context['mokymo_instrukcijos'] = models.MokymuPasirasymas.objects.filter(user=self.request.user, status=0)
        context['kitu_doc'] = models.KituDocPasirasymas.objects.filter(user=self.request.user, status=0)
        context['civiline_sauga'] = models.CivilineSaugaPasirasymas.objects.filter(user=self.request.user, status=0)
        return context


class UserInstructionSignUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.UserInstructionSign
    form_class = forms.UserInstructionSignForm
    template_name = 'main/user_instruction_detail.html'

    def get_object(self, queryset=None):
        uuid = self.kwargs.get('uuid')
        return get_object_or_404(models.UserInstructionSign, uuid=uuid)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['instruction'] = self.object.instruction
        context['pdf_url'] = self.object.instruction.pdf  # Correctly set the PDF URL
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.status = 1
        form.instance.date_signed = datetime.now()
        form.instance.next_sign = datetime.now() + timedelta(int(self.object.instruction.periodiskumas))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('user_instructions')


class CivilineSaugaSignView(LoginRequiredMixin, generic.UpdateView):
    model = models.CivilineSaugaPasirasymas
    form_class = forms.UserInstructionSignForm
    template_name = 'main/user_instruction_detail.html'

    def get_object(self, queryset=None):
        uuid = self.kwargs.get('uuid')
        return get_object_or_404(models.CivilineSaugaPasirasymas, uuid=uuid)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['instruction'] = self.object.instruction
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.status = 1
        form.instance.date_signed = datetime.now()
        form.instance.next_sign = datetime.now() + timedelta(int(self.object.instruction.periodiskumas))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('user_instructions')


class PriesgaisrinioSignView(LoginRequiredMixin, generic.UpdateView):
    model = models.PriesgaisriniuPasirasymas
    form_class = forms.UserInstructionSignForm
    template_name = 'main/user_instruction_detail.html'

    def get_object(self, queryset=None):
        uuid = self.kwargs.get('uuid')
        return get_object_or_404(models.PriesgaisriniuPasirasymas, uuid=uuid)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['instruction'] = self.object.instruction
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.status = 1
        form.instance.date_signed = datetime.now()
        form.instance.next_sign = datetime.now() + timedelta(int(self.object.instruction.periodiskumas))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('user_instructions')

    

class MokymuSignView(LoginRequiredMixin, generic.UpdateView):
    model = models.MokymuPasirasymas
    form_class = forms.UserInstructionSignForm
    template_name = 'main/user_instruction_detail.html'

    def get_object(self, queryset=None):
        uuid = self.kwargs.get('uuid')
        return get_object_or_404(models.MokymuPasirasymas, uuid=uuid)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['instruction'] = self.object.instruction
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.status = 1
        form.instance.date_signed = datetime.now()
        form.instance.next_sign = datetime.now() + timedelta(int(self.object.instruction.periodiskumas))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('user_instructions')


class KituDocSignView(LoginRequiredMixin, generic.UpdateView):
    model = models.KituDocPasirasymas
    form_class = forms.UserInstructionSignForm
    template_name = 'main/user_instruction_detail.html'

    def get_object(self, queryset=None):
        uuid = self.kwargs.get('uuid')
        return get_object_or_404(models.KituDocPasirasymas, uuid=uuid)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['instruction'] = self.object.instruction
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.status = 1
        form.instance.date_signed = datetime.now()
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
    form_class = forms.UserEditForm

    def get_object(self, queryset=None):
        uuid = self.kwargs.get('uuid')
        return get_object_or_404(models.User, uuid=uuid)

    def get_success_url(self):
        return reverse_lazy('menu')

    def form_valid(self, form):
        user = form.save(commit=False)
        password = self.request.POST.get('password')

        # Check if the password field is not empty before updating
        if password:
            user.set_password(password)

        user.save()

        return super().form_valid(form)



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


class DarbuSaugosZurnalas(LoginRequiredMixin, generic.ListView):
    model = models.UserInstructionSign
    template_name ='main/darbu_saugos_zurnalas.html'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_supervisor:
            raise PermissionDenied("You do not have permission to access this view.")
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = True
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset()
        company = self.request.user.company
        queryset = queryset.filter(user__company=company)
        
        query = self.request.GET.get('query')
        if query:
            queryset = queryset.filter(
                Q(user__position__name__icontains=query) |
                Q(user__email__icontains=query) |
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query)
            )
        print("Queryset:", queryset)  
        return queryset
    
class CivilinesSaugosZurnalas(LoginRequiredMixin, generic.ListView):
    model = models.CivilineSaugaPasirasymas
    template_name ='main/civilines_saugos_zurnalas.html'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_supervisor:
            raise PermissionDenied("You do not have permission to access this view.")
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = True
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset()
        company = self.request.user.company
        queryset = queryset.filter(user__company=company)
        
        query = self.request.GET.get('query')
        if query:
            queryset = queryset.filter(
                Q(user__position__name__icontains=query) |
                Q(user__email__icontains=query) |
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query)
            )
        print("Queryset:", queryset)  
        return queryset


class MokymuZurnalas(LoginRequiredMixin, generic.ListView):
    model = models.Mokymai
    template_name ='main/mokymu_zurnalas.html'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_supervisor:
            raise PermissionDenied("You do not have permission to access this view.")
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = True
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset()
        company = self.request.user.company
        queryset = queryset.filter(imone=company)
        return queryset

class MokymuPasirasymasList(generic.ListView):
    model = models.MokymuPasirasymas
    template_name = 'main/mokymu_pasirasymas_list.html'  # Update with your template name

    def get_queryset(self):
        # Assuming you're passing the UUID through URL parameter
        uuid = self.kwargs['uuid']
        
        # Fetch the MokymuPasirasymas objects based on UUID
        queryset = models.MokymuPasirasymas.objects.filter(instruction__uuid=uuid)
        
        return queryset



class KituDocZurnalas(LoginRequiredMixin, generic.ListView):
    model = models.KituDocPasirasymas
    template_name ='main/kitu_doc_zurnalas.html'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_supervisor:
            raise PermissionDenied("You do not have permission to access this view.")
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = True
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset()
        company = self.request.user.company
        queryset = queryset.filter(user__company=company)
        
        query = self.request.GET.get('query')
        if query:
            queryset = queryset.filter(
                Q(user__position__name__icontains=query) |
                Q(user__email__icontains=query) |
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query)
            )
        print("Queryset:", queryset)  
        return queryset
    

class PriesgaisrinesSaugosZurnalas(LoginRequiredMixin, generic.ListView):
    model = models.PriesgaisriniuPasirasymas
    template_name ='main/priesgaisrines_saugos_zurnalas.html'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_supervisor:
            raise PermissionDenied("You do not have permission to access this view.")
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = True
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset()
        company = self.request.user.company
        queryset = queryset.filter(user__company=company)
        
        query = self.request.GET.get('query')
        if query:
            queryset = queryset.filter(
                Q(user__position__name__icontains=query) |
                Q(user__email__icontains=query) |
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query)
            )
        
        return queryset
    

class SveikatosTikrinimoGrafikas(LoginRequiredMixin, generic.ListView):
    model = models.User
    template_name ='main/sveikatos_tikrinimo_grafikas.html'


class SupervisorEditUserView(LoginRequiredMixin, generic.UpdateView):
    model = models.User
    form_class = forms.SupervisorEditUserForm
    template_name = 'main/supervisor_edit_user.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.user = self.request.user
        form.fields['position'].queryset = models.Position.objects.filter(company=self.request.user.company)
        form.fields['instructions'].queryset = models.Instruction.objects.filter(company=self.request.user.company)
        form.fields['mokymai'].queryset = models.Mokymai.objects.filter(imone=self.request.user.company)
        form.fields['priesgaisrines'].queryset = models.PriesgiasrinesInstrukcijos.objects.filter(imone=self.request.user.company)
        form.fields['kiti_dokumentai'].queryset = models.KitiDokumentai.objects.filter(imone=self.request.user.company)
        form.fields['civiline_sauga'].queryset = models.CivilineSauga.objects.filter(imone=self.request.user.company)
        return form

    def get_object(self, queryset=None):
        uuid = self.kwargs.get('uuid')
        return get_object_or_404(models.User, uuid=uuid)
    
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
        password = self.request.POST.get('password')
        instructions = form.cleaned_data.get('instructions')
        priesgaisrines = form.cleaned_data.get('priesgaisrines')
        civiline_sauga = form.cleaned_data.get('civiline_sauga')
        mokymai = form.cleaned_data.get('mokymai')
        kitidokumentai = form.cleaned_data.get('kiti_dokumentai')
        med_patikros_data = form.cleaned_data.get('med_patikros_data')
        med_patikros_periodas = form.cleaned_data.get('med_patikros_periodas')
        priesgaisrinesinstrukcijospasirasymai = models.PriesgaisriniuPasirasymas.objects.filter(user=user)
        civilinesaugapasirasymai = models.CivilineSaugaPasirasymas.objects.filter(user=user)
        mokymaipasirasymai = models.MokymuPasirasymas.objects.filter(user=user)
        kitidokumentaipasirasymai = models.KituDocPasirasymas.objects.filter(user=user)      
        existing_signs = models.UserInstructionSign.objects.filter(user=user)

        if password:
            user.set_password(password)

        if med_patikros_data and med_patikros_periodas:
            if isinstance(med_patikros_periodas, str):
                med_patikros_periodas = int(med_patikros_periodas)
            timedelta_periodas = timedelta(days=med_patikros_periodas / 12 * 365)
            user.sekanti_med_patikros_data = med_patikros_data + timedelta_periodas

        user.save()

        for instruction in instructions:
            existing_sign = existing_signs.filter(instruction=instruction).first()
            if existing_sign:
                existing_sign.save()
            else:
                models.UserInstructionSign.objects.create(
                    user=user,
                    instruction=instruction,
                )

        for instruction in priesgaisrines:
            existing_sign = priesgaisrinesinstrukcijospasirasymai.filter(instruction=instruction).first()
            if existing_sign:
                existing_sign.save()
            else:
                models.PriesgaisriniuPasirasymas.objects.create(
                    user=user,
                    instruction=instruction,
                )
        
        for instruction in civiline_sauga:
            existing_sign = civilinesaugapasirasymai.filter(instruction=instruction).first()
            if existing_sign:
                existing_sign.save()
            else:
                models.CivilineSaugaPasirasymas.objects.create(
                    user=user,
                    instruction=instruction,
                )

        for instruction in mokymai:
            existing_sign = mokymaipasirasymai.filter(instruction=instruction).first()
            if existing_sign:
                existing_sign.save()
            else:
                models.MokymuPasirasymas.objects.create(
                    user=user,
                    instruction=instruction,
                )

        for instruction in kitidokumentai:
            existing_sign = kitidokumentaipasirasymai.filter(instruction=instruction).first()
            if existing_sign:
                existing_sign.save()
            else:
                models.KituDocPasirasymas.objects.create(
                    user=user,
                    instruction=instruction,
                )

        return super().form_valid(form)
    

class DokumentuListView(LoginRequiredMixin, generic.ListView):
    model = models.Instruction
    template_name = 'main/dokumentai_list.html'
    context_object_name = 'dokumentai'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['priesrines_instrukcijos'] = models.PriesgiasrinesInstrukcijos.objects.filter(imone=self.request.user.company)
        context['mokymo_instrukcijos'] = models.Mokymai.objects.filter(imone=self.request.user.company)
        context['kitu_doc'] = models.KitiDokumentai.objects.filter(imone=self.request.user.company)
        context['civiline_sauga'] = models.CivilineSauga.objects.filter(imone=self.request.user.company)
        return context
    

class UserInstructionReviewView(LoginRequiredMixin, generic.UpdateView):
    model = models.Instruction
    form_class = forms.RenderPDFForm
    template_name = 'main/dokumento_view.html'

    def get_object(self, queryset=None):
        uuid = self.kwargs.get('uuid')
        return get_object_or_404(models.Instruction, uuid=uuid)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['instruction'] = self.object
        return context


class CivilineSaugaReviewView(LoginRequiredMixin, generic.UpdateView):
    model = models.CivilineSauga
    form_class = forms.RenderPDFForm
    template_name = 'main/dokumento_view.html'

    def get_object(self, queryset=None):
        uuid = self.kwargs.get('uuid')
        return get_object_or_404(models.CivilineSauga, uuid=uuid)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['instruction'] = self.object
        return context


class PriesgaisrinioReviewView(LoginRequiredMixin, generic.UpdateView):
    model = models.PriesgiasrinesInstrukcijos
    form_class = forms.RenderPDFForm
    template_name = 'main/dokumento_view.html'

    def get_object(self, queryset=None):
        uuid = self.kwargs.get('uuid')
        return get_object_or_404(models.PriesgiasrinesInstrukcijos, uuid=uuid)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['instruction'] = self.object
        return context
    

class MokymuReviewView(LoginRequiredMixin, generic.UpdateView):
    model = models.Mokymai
    form_class = forms.RenderPDFForm
    template_name = 'main/dokumento_view.html'

    def get_object(self, queryset=None):
        uuid = self.kwargs.get('uuid')
        return get_object_or_404(models.Mokymai, uuid=uuid)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['instruction'] = self.object
        return context


class KituDocReviewView(LoginRequiredMixin, generic.UpdateView):
    model = models.KitiDokumentai
    form_class = forms.RenderPDFForm
    template_name = 'main/dokumento_view.html'

    def get_object(self, queryset=None):
        uuid = self.kwargs.get('uuid')
        return get_object_or_404(models.KitiDokumentai, uuid=uuid)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['instruction'] = self.object
        return context
