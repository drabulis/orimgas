from typing import Any
from django.shortcuts import render
from django.contrib.auth.mixins import  LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.db.models.query import QuerySet, Q
from django.http import HttpResponse, JsonResponse
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.views import View
from django.http import FileResponse
from . import models, forms
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.utils import translation
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from django.utils.dateparse import parse_date
import os
from django.utils import timezone
from django.db import transaction


def log_user_instruction_activity(user, instruction_name, ip_address):
    # Define the path for the log file
    log_file_path = os.path.join(settings.BASE_DIR, 'user_instruction_log.log')
    
    # Create a log message with timestamp
    log_message = (
        f"{timezone.now()} - Vartotojas {user.first_name} {user.last_name} "
        f"({user.email}) susipažino/pasirašė '{instruction_name}' iš IP: {ip_address}\n"
    )
    
    # Append the log message to the file
    with open(log_file_path, 'a') as log_file:
        log_file.write(log_message)

class UserMeniuView(LoginRequiredMixin, generic.ListView):
    model = models.UserInstructionSign
    template_name = 'menu_bootstrap.html'
    paginate_by = 10000
    # context_object_name = 'instructions'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user, status=0)
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # All pending instructions by type (status=0 means pending/unsigned)
        context['priesrines_instrukcijos'] = models.PriesgaisriniuPasirasymas.objects.filter(user=user, status=0)
        context['mokymo_instrukcijos'] = models.MokymuPasirasymas.objects.filter(user=user, status=0)
        context['kitu_doc'] = models.KituDocPasirasymas.objects.filter(user=user, status=0)
        context['civiline_sauga'] = models.CivilineSaugaPasirasymas.objects.filter(user=user, status=0)
        context['asmenines_apsaugos_priemones'] = models.AAPPasirasymas.objects.filter(user=user, status=0)
        
        # Calculate statistics for dashboard
        # Total pending instructions
        pending_count = (
            context['object_list'].count() +
            context['priesrines_instrukcijos'].count() +
            context['mokymo_instrukcijos'].count() +
            context['kitu_doc'].count() +
            context['civiline_sauga'].count() +
            context['asmenines_apsaugos_priemones'].count()
        )
        context['pending_instructions'] = pending_count
        
        # Total signed instructions (status=1 means signed)
        signed_count = (
            models.UserInstructionSign.objects.filter(user=user, status=1).count() +
            models.PriesgaisriniuPasirasymas.objects.filter(user=user, status=1).count() +
            models.MokymuPasirasymas.objects.filter(user=user, status=1).count() +
            models.KituDocPasirasymas.objects.filter(user=user, status=1).count() +
            models.CivilineSaugaPasirasymas.objects.filter(user=user, status=1).count() +
            models.AAPPasirasymas.objects.filter(user=user, status=1).count()
        )
        context['signed_instructions'] = signed_count
        
        # Total instructions (both signed and pending)
        context['total_instructions'] = pending_count + signed_count
        
        # Expired instructions (status=2 typically means expired/overdue)
        expired_count = (
            models.UserInstructionSign.objects.filter(user=user, status=2).count() +
            models.PriesgaisriniuPasirasymas.objects.filter(user=user, status=2).count() +
            models.MokymuPasirasymas.objects.filter(user=user, status=2).count() +
            models.KituDocPasirasymas.objects.filter(user=user, status=2).count() +
            models.CivilineSaugaPasirasymas.objects.filter(user=user, status=2).count() +
            models.AAPPasirasymas.objects.filter(user=user, status=2).count()
        )
        context['expired_instructions'] = expired_count
        
        context['user'] = user
        return context    


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
    template_name = 'main/user_add_bootstrap.html'
    success_url = reverse_lazy('my_company_users')

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_supervisor:
            raise PermissionDenied("Tau čia negalima!")
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        selected_language = self.request.POST.get('kalba') or self.request.GET.get('kalba') or form.initial.get('kalba')
        company = self.request.user.company
        if selected_language:
            form.fields['instructions'].queryset = models.Instruction.objects.filter(company=company, kalba=selected_language).order_by('name')
            form.fields['priesgaisrines'].queryset = models.PriesgiasrinesInstrukcijos.objects.filter(imone=company, kalba=selected_language).order_by('pavadinimas')
            form.fields['mokymai'].queryset = models.Mokymai.objects.filter(imone=company, kalba=selected_language).order_by('pavadinimas')
            form.fields['kiti_dokumentai'].queryset = models.KitiDokumentai.objects.filter(imone=company, kalba=selected_language).order_by('pavadinimas')
            form.fields['civiline_sauga'].queryset = models.CivilineSauga.objects.filter(imone=company, kalba=selected_language).order_by('pavadinimas')
        else:
            form.fields['instructions'].queryset = models.Instruction.objects.filter(company=company).order_by('name')
            form.fields['priesgaisrines'].queryset = models.PriesgiasrinesInstrukcijos.objects.filter(imone=company).order_by('pavadinimas')
            form.fields['mokymai'].queryset = models.Mokymai.objects.filter(imone=company).order_by('pavadinimas')
            form.fields['kiti_dokumentai'].queryset = models.KitiDokumentai.objects.filter(imone=company).order_by('pavadinimas')
            form.fields['civiline_sauga'].queryset = models.CivilineSauga.objects.filter(imone=company).order_by('pavadinimas')
        form.fields['position'].queryset = models.Position.objects.filter(company=company).order_by('name')
        form.fields['AsmeninesApsaugosPriemones'].queryset = company.AAP.order_by('pavadinimas')
        form.fields['skyrius'].queryset = models.Skyrius.objects.filter(company=company).order_by('pavadinimas')
        form.fields['AsmeninesApsaugosPriemones'].initial = []
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # For AddUserView, there is no user object yet
        context['assigned_instructions'] = []
        context['priesgaisrines'] = []
        context['civiline_sauga'] = []
        context['mokymai'] = []
        context['kiti_dokumentai'] = []
        context['AAP'] = []
        return context
    
    def form_valid(self, form):
        form.instance.company = self.request.user.company
        med_patikros_data = form.cleaned_data.get('med_patikros_data')
        med_patikros_periodas = form.cleaned_data.get('med_patikros_periodas')


        if med_patikros_data and med_patikros_periodas:
            if isinstance(med_patikros_periodas, str):
                med_patikros_periodas = int(med_patikros_periodas)
            timedelta_periodas = timedelta(days=med_patikros_periodas / 12 * 365)
            form.instance.sekanti_med_patikros_data = med_patikros_data + timedelta_periodas

        return super().form_valid(form)


class DemoAddUserView(AddUserView):
    """Bootstrap demo version of AddUserView (read-only access from demo page)."""

    template_name = 'main/user_add_bootstrap.html'
    success_url = reverse_lazy('menu_bootstrap')


class UserInstructionSignView(LoginRequiredMixin, generic.ListView):
    model = models.UserInstructionSign
    template_name = 'main/user_instructions.html'
    paginate_by = 10000

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
        context['asmenines_apsaugos_priemones'] = models.AAPPasirasymas.objects.filter(user=self.request.user, status=0)
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
        ip_address = self.get_client_ip(self.request)
        log_user_instruction_activity(self.request.user, self.object.instruction.name, ip_address)
        
        return super().form_valid(form)

    def get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]  # Take the first IP in case of multiple proxies
        else:
            ip = request.META.get('REMOTE_ADDR')  # Fallback to REMOTE_ADDR
        
        return ip

    def get_success_url(self):
        return reverse_lazy('menu')


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
        
        ip_address = self.get_client_ip(self.request)
        log_user_instruction_activity(self.request.user, self.object.instruction.pavadinimas, ip_address)
        
        return super().form_valid(form)

    def get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]  # Take the first IP in case of multiple proxies
        else:
            ip = request.META.get('REMOTE_ADDR')  # Fallback to REMOTE_ADDR
        
        return ip

    def get_success_url(self):
        return reverse_lazy('menu')


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
        
        ip_address = self.get_client_ip(self.request)
        log_user_instruction_activity(self.request.user, self.object.instruction.pavadinimas, ip_address)
        
        return super().form_valid(form)

    def get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]  # Take the first IP in case of multiple proxies
        else:
            ip = request.META.get('REMOTE_ADDR')  # Fallback to REMOTE_ADDR
        
        return ip

    def get_success_url(self):
        return reverse_lazy('menu')

    

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
        ip_address = self.get_client_ip(self.request)
        log_user_instruction_activity(self.request.user, self.object.instruction.pavadinimas, ip_address)
        
        return super().form_valid(form)

    def get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]  # Take the first IP in case of multiple proxies
        else:
            ip = request.META.get('REMOTE_ADDR')  # Fallback to REMOTE_ADDR
        
        return ip

    def get_success_url(self):
        return reverse_lazy('menu')


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
        ip_address = self.get_client_ip(self.request)
        log_user_instruction_activity(self.request.user, self.object.instruction.pavadinimas, ip_address)
        
        return super().form_valid(form)

    def get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]  # Take the first IP in case of multiple proxies
        else:
            ip = request.META.get('REMOTE_ADDR')  # Fallback to REMOTE_ADDR
        
        return ip

    def get_success_url(self):
        return reverse_lazy('menu')



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
    paginate_by = 10000

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_supervisor:
            raise PermissionDenied("You do not have permission to access this view.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = True

        # Add sorting context
        context["sort_by"] = self.request.GET.get('sort_by', 'first_name')
        context["sort_order"] = self.request.GET.get('sort_order', 'asc')

        # Keep the query in the context to persist the search
        context["query"] = self.request.GET.get('query', '')

        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('query', '')
        company = self.request.user.company
        skyrius = self.request.user.skyrius

        # Apply the initial company filter
        if self.request.user.skyrius is not None:
            queryset = queryset.filter(company=company, skyrius=skyrius)
        else:
            queryset = queryset.filter(company=company)

        # Debugging: Print the queryset count to check pagination handling
        print(f"Queryset count before filtering: {queryset.count()}")

        if query:
            queryset = queryset.filter(
                Q(position__name__icontains=query)
                | Q(email__icontains=query)
                | Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
            )

        # Sorting logic
        sort_by = self.request.GET.get('sort_by', 'first_name')
        sort_order = self.request.GET.get('sort_order', 'asc')
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'
        queryset = queryset.order_by(sort_by)

        # Debugging: Print the final queryset count after filtering
        print(f"Queryset count after filtering: {queryset.count()}")

        return queryset

    def get(self, request, *args, **kwargs):
        if 'generate_pdf' in request.GET:
            return self.generate_pdf(request)
        return super().get(request, *args, **kwargs)

    def generate_pdf(self, request):
        # Get the filtered queryset
        queryset = self.get_queryset()

        # Define the table structure
        table_headers = ['Vardas Pavardė', 'Gimimo metai', 'El. paštas', 'Pareigos', 'Aktyvus']
        table_data = []

        for user in queryset:
            row = [
                user.get_full_name(),
                user.date_of_birth,
                user.email,
                user.position.name if user.position else 'N/A',
                'Aktyvus' if user.is_active else 'Neaktyvus',
            ]
            table_data.append(row)

        context = {
            'title': 'Įmonės Darbuotojai',
            'headers': table_headers,
            'data': table_data,
            'company_name': request.user.company.name,
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M')
        }

        # Render the PDF
        html_string = render_to_string('pdf_template.html', context)
        html = HTML(string=html_string)

        with tempfile.NamedTemporaryFile(delete=True) as output:
            html.write_pdf(target=output.name)
            output.seek(0)
            response = HttpResponse(output.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="Įmonės darbuotojai.pdf"'
            return response


class DarbuSaugosZurnalas(LoginRequiredMixin, generic.ListView):
    model = models.UserInstructionSign
    template_name = 'main/darbu_saugos_zurnalas.html'
    paginate_by = 10000

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_supervisor:
            raise PermissionDenied("You do not have permission to access this view.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = True
        context["sort_by"] = self.request.GET.get('sort_by', 'user__first_name')
        context["sort_order"] = self.request.GET.get('sort_order', 'asc')
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        company = self.request.user.company
        queryset = queryset.filter(user__company=company)

        # Handle search query
        query = self.request.GET.get('query')
        if query:
            queryset = queryset.filter(
                Q(user__position__name__icontains=query) |
                Q(user__email__icontains=query) |
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query)
            )

        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date:
            queryset = queryset.filter(date_signed__gte=parse_date(start_date))
        if end_date:
            queryset = queryset.filter(date_signed__lte=parse_date(end_date))
        
        # Handle sorting
        sort_by = self.request.GET.get('sort_by', 'user__first_name')
        sort_order = self.request.GET.get('sort_order', 'asc')
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'
        queryset = queryset.order_by(sort_by)

        return queryset

    def generate_pdf(self, request):
        # Get the filtered queryset
        queryset = self.get_queryset()

        # Define the table structure
        table_headers = [
            'Instruktuojamojo vardas ir pavardė',
            'Instruktuojamojo gimimo data',
            'Instruktuojamojo pareigos',
            'Instrukcijos Nr.',
            'Instruktavimo pavadinimas',
            'Instruktuojamojo parašas',
            'Pasirašymo data',
            'Sekančio pasirašymo data',
        ]
        table_data = []

        for sign in queryset:
            row = [
                sign.user.get_full_name(),
                sign.user.date_of_birth,
                sign.user.position.name if sign.user.position else 'N/A',
                sign.instruction.name if sign.instruction else 'N/A',
                'Pirminis' if sign.instruktavimo_tipas==0 else 'Periodinis',
                sign.get_status_display(),
                sign.date_signed if sign.date_signed else 'N/A',
                sign.next_sign if sign.next_sign else 'N/A',
            ]
            table_data.append(row)

        context = {
            'title': 'Darbuotojų saugos ir sveikatos instruktavimų darbo vietoje registras',
            'headers': table_headers,
            'data': table_data,
            'company_name': request.user.company.name,
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M')
        }

         # Render the PDF
        html_string = render_to_string('pdf_template.html', context)
        html = HTML(string=html_string)

        with tempfile.NamedTemporaryFile(delete=True) as output:
            html.write_pdf(target=output.name)
            output.seek(0)
            response = HttpResponse(output.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="Įmonės darbuotojai.pdf"'
            return response


    def get(self, request, *args, **kwargs):
        if 'generate_pdf' in request.GET:
            return self.generate_pdf(request)
        return super().get(request, *args, **kwargs)
   


class CivilinesSaugosZurnalas(LoginRequiredMixin, generic.ListView):
    model = models.CivilineSaugaPasirasymas
    template_name ='main/civilines_saugos_zurnalas.html'
    paginate_by = 10000

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
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

    # Apply filtering by name or other fields
        if query:
            queryset = queryset.filter(
                Q(user__position__name__icontains=query) |
                Q(user__email__icontains=query) |
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) 
            )
            return queryset

        # Apply date filtering
        if start_date:
            queryset = queryset.filter(date_signed__gte=parse_date(start_date))
        if end_date:
            queryset = queryset.filter(date_signed__lte=parse_date(end_date))
        
        return queryset

    def generate_pdf(self, request):
        queryset = self.get_queryset()

        table_headers = [
            'Instruktuojamojo vardas ir pavardė',
            'Instruktuojamojo gimimo data',
            'Instruktuojamojo pareigos',
            'Instrukcijos Nr.',
            'Instruktavimo pavadinimas',
            'Instruktuojamojo parašas',
            'Pasirašymo data',
            'Sekančio pasirašymo data',
        ]
        table_data = []

        for sign in queryset:
            row = [
                sign.user.get_full_name(),
                sign.user.date_of_birth,
                sign.user.position.name if sign.user.position else 'N/A',
                sign.instruction.pavadinimas if sign.instruction else 'N/A',
                'Pirminis' if sign.instruktavimo_tipas==0 else 'Periodinis',
                'Pasirašyta' if sign.status == 1 else 'Ne Pasirašyta',
                sign.date_signed if sign.date_signed else 'N/A',
                sign.next_sign if sign.next_sign else 'N/A',
            ]
            table_data.append(row)

        context = {
            'title': 'Civilinės saugos instruktavimų registracijos žurnalas',
            'headers': table_headers,
            'data': table_data,
            'company_name': request.user.company.name,
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M')
        }

        # Render the PDF
        html_string = render_to_string('pdf_template.html', context)
        html = HTML(string=html_string)

        with tempfile.NamedTemporaryFile(delete=True) as output:
            html.write_pdf(target=output.name)
            output.seek(0)
            response = HttpResponse(output.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="Įmonės darbuotojai.pdf"'
            return response


    def get(self, request, *args, **kwargs):
        if 'generate_pdf' in request.GET:
            return self.generate_pdf(request)
        return super().get(request, *args, **kwargs) 

class MokymuZurnalas(LoginRequiredMixin, generic.ListView):
    model = models.Mokymai
    template_name ='main/mokymu_zurnalas.html'
    paginate_by = 10000

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
    template_name = 'main/mokymu_pasirasymas_list.html'

    def get_queryset(self):
        uuid = self.kwargs['uuid']
        queryset = models.MokymuPasirasymas.objects.filter(instruction__uuid=uuid)
        
        return queryset

    def generate_pdf(self, request):
        queryset = self.get_queryset()

        table_headers = [
            'Vardas ir pavardė',
            'Gimimo data',
            'Pareigos',
            'Mokymo programa',
            'Vertinimo rezultatas',
            'Pasirašymo data',
            'Sekančio pasirašymo data',
        ]
        table_data = []

        for sign in queryset:
            row = [
                sign.user.get_full_name(),
                sign.user.date_of_birth,
                sign.user.position.name if sign.user.position else 'N/A',
                sign.instruction.pavadinimas if sign.instruction else 'N/A',
                'Neįskaityta' if sign.status == 0 else 'Įskaityta',
                sign.date_signed if sign.date_signed else 'N/A',
                sign.next_sign if sign.next_sign else 'N/A',
            ]
            table_data.append(row)

        context = {
        'title': 'Atestavimo protokolas',
        'headers': table_headers,
        'data': table_data,
        'company_name': request.user.company.name,
        'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M')
    }

        # Render the PDF
        html_string = render_to_string('pdf_template.html', context)
        html = HTML(string=html_string)

        with tempfile.NamedTemporaryFile(delete=True) as output:
            html.write_pdf(target=output.name)
            output.seek(0)
            response = HttpResponse(output.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="Įmonės darbuotojai.pdf"'
            return response


    def get(self, request, *args, **kwargs):
        if 'generate_pdf' in request.GET:
            return self.generate_pdf(request)
        return super().get(request, *args, **kwargs) 


class KituDocZurnalas(LoginRequiredMixin, generic.ListView):
    model = models.KitiDokumentai
    template_name ='main/kitu_doc_zurnalas.html'
    paginate_by = 10000

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

class KituDocPasirasymuZurnalas(LoginRequiredMixin, generic.ListView):
    model = models.KituDocPasirasymas
    template_name = 'main/kitu_doc_pasirasymu_zurnalas.html'
    paginate_by = 10000

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_supervisor:
            raise PermissionDenied("You do not have permission to access this view.")
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['uuid'] = self.kwargs['uuid']
        return context
    
    def get_queryset(self):
        uuid = self.kwargs['uuid']
        queryset = models.KituDocPasirasymas.objects.filter(instruction__uuid=uuid)    
        return queryset

    def generate_pdf(self, request):
        queryset = self.get_queryset()

        table_headers = [
            'Vardas ir pavardė',
            'Gimimo data',
            'Pareigos',
            'Dokumento pavadinimas',
            'Instruktuojamojo parašas',
            'Pasirašymo data',
        ]
        table_data = []

        for sign in queryset:
            row = [
                sign.user.get_full_name(),
                sign.user.date_of_birth,
                sign.user.position.name if sign.user.position else 'N/A',
                sign.instruction.pavadinimas if sign.instruction else 'N/A',
                'Pasirašyta' if sign.status == 1 else 'Ne Pasirašyta',
                sign.date_signed if sign.date_signed else 'N/A',
            ]
            table_data.append(row)

        context = {
            'title': 'Kitų dokumentų protokolas',
            'headers': table_headers,
            'data': table_data,
            'company_name': request.user.company.name,
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        # Render the PDF
        html_string = render_to_string('pdf_template.html', context)
        html = HTML(string=html_string)

        with tempfile.NamedTemporaryFile(delete=True) as output:
            html.write_pdf(target=output.name)
            output.seek(0)
            response = HttpResponse(output.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="Kitų dokumentų protokolas.pdf"'
            return response

    def get(self, request, *args, **kwargs):
        if 'generate_pdf' in request.GET:
            return self.generate_pdf(request)
        return super().get(request, *args, **kwargs) 



class PriesgaisrinesSaugosZurnalas(LoginRequiredMixin, generic.ListView):
    model = models.PriesgaisriniuPasirasymas
    template_name ='main/priesgaisrines_saugos_zurnalas.html'
    paginate_by = 10000

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
        
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date:
            queryset = queryset.filter(date_signed__gte=parse_date(start_date))
        if end_date:
            queryset = queryset.filter(date_signed__lte=parse_date(end_date))
        
        return queryset

    def generate_pdf(self, request):
        # Get the filtered queryset
        queryset = self.get_queryset()

        # Define the table structure
        table_headers = [
            'Instruktuojamojo vardas ir pavardė',
            'Instruktuojamojo gimimo data',
            'Instruktuojamojo pareigos',
            'Instrukcijos Nr.',
            'Instruktavimo pavadinimas',
            'Instruktuojamojo parašas',
            'Pasirašymo data',
            'Sekančio pasirašymo data',
        ]
        table_data = []

        for sign in queryset:
            row = [
                sign.user.get_full_name(),
                sign.user.date_of_birth,
                sign.user.position.name if sign.user.position else 'N/A',
                sign.instruction.pavadinimas if sign.instruction else 'N/A',
                'Įvadinis' if sign.instruktavimo_tipas==0 else 'Periodinis',
                'Pasirašyta' if sign.status == 1 else 'Nepasirašyta',
                sign.date_signed if sign.date_signed else 'N/A',
                sign.next_sign if sign.next_sign else 'N/A',
            ]
            table_data.append(row)

        context = {
            'title': 'Gaisrinės saugos instruktažų registracijos žurnalas',
            'headers': table_headers,
            'data': table_data,
            'company_name': request.user.company.name,
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        # Render the PDF
        html_string = render_to_string('pdf_template.html', context)
        html = HTML(string=html_string)

        with tempfile.NamedTemporaryFile(delete=True) as output:
            html.write_pdf(target=output.name)
            output.seek(0)
            response = HttpResponse(output.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="Gaisrinės saugos.pdf"'
            return response

    def get(self, request, *args, **kwargs):
        if 'generate_pdf' in request.GET:
            return self.generate_pdf(request)
        return super().get(request, *args, **kwargs)

class SveikatosTikrinimoGrafikas(LoginRequiredMixin, generic.ListView):
    model = models.User
    template_name ='main/sveikatos_tikrinimo_grafikas.html'
    paginate_by = 10000

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_supervisor:
            raise PermissionDenied("You do not have permission to access this view.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = True

        # Add sorting context
        context["sort_by"] = self.request.GET.get('sort_by', 'first_name')
        context["sort_order"] = self.request.GET.get('sort_order', 'asc')

        # Keep the query in the context to persist the search
        context["query"] = self.request.GET.get('query', '')

        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('query', '')
        company = self.request.user.company

        # Apply the initial company filter
        queryset = queryset.filter(company=company)

        # Debugging: Print the queryset count to check pagination handling
        print(f"Queryset count before filtering: {queryset.count()}")

        if query:
            queryset = queryset.filter(
                Q(position__name__icontains=query)
                | Q(email__icontains=query)
                | Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
            )

        # Sorting logic
        sort_by = self.request.GET.get('sort_by', 'first_name')
        sort_order = self.request.GET.get('sort_order', 'asc')
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'
        queryset = queryset.order_by(sort_by)

        # Debugging: Print the final queryset count after filtering
        print(f"Queryset count after filtering: {queryset.count()}")

        return queryset

    def get(self, request, *args, **kwargs):
        if 'generate_pdf' in request.GET:
            return self.generate_pdf(request)
        return super().get(request, *args, **kwargs)

    def generate_pdf(self, request):
        # Get the filtered queryset
        queryset = self.get_queryset()

        # Define the table structure
        table_headers = ['Vardas Pavardė', 'Gimimo metai', 'El. paštas', 'Pareigos', 'Aktyvus']
        table_data = []

        for user in queryset:
            row = [
                user.get_full_name(),
                user.date_of_birth,
                user.email,
                user.position.name if user.position else 'N/A',
                'Aktyvus' if user.is_active else 'Neaktyvus',
            ]
            table_data.append(row)

        context = {
            'title': 'Įmonės Darbuotojai',
            'headers': table_headers,
            'data': table_data,
            'company_name': request.user.company.name,
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M')
        }

        # Render the PDF
        html_string = render_to_string('pdf_template.html', context)
        html = HTML(string=html_string)

        with tempfile.NamedTemporaryFile(delete=True) as output:
            html.write_pdf(target=output.name)
            output.seek(0)
            response = HttpResponse(output.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="Įmonės darbuotojai.pdf"'
            return response



class SupervisorEditUserView(LoginRequiredMixin, generic.UpdateView):
    model = models.User
    form_class = forms.SupervisorEditUserForm
    template_name = 'main/supervisor_edit_user.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        selected_language = self.request.POST.get('kalba') or self.request.GET.get('kalba') or form.initial.get('kalba')
        company = self.request.user.company
        user_to_edit = self.get_object()
        
        if selected_language:
            form.fields['instructions'].queryset = models.Instruction.objects.filter(company=company, kalba=selected_language)
            form.fields['priesgaisrines'].queryset = models.PriesgiasrinesInstrukcijos.objects.filter(imone=company, kalba=selected_language)
            form.fields['mokymai'].queryset = models.Mokymai.objects.filter(imone=company, kalba=selected_language)
            form.fields['kiti_dokumentai'].queryset = models.KitiDokumentai.objects.filter(imone=company, kalba=selected_language)
            form.fields['civiline_sauga'].queryset = models.CivilineSauga.objects.filter(imone=company, kalba=selected_language)
        else:
            form.fields['instructions'].queryset = models.Instruction.objects.filter(company=company)
            form.fields['priesgaisrines'].queryset = models.PriesgiasrinesInstrukcijos.objects.filter(imone=company)
            form.fields['mokymai'].queryset = models.Mokymai.objects.filter(imone=company)
            form.fields['kiti_dokumentai'].queryset = models.KitiDokumentai.objects.filter(imone=company)
            form.fields['civiline_sauga'].queryset = models.CivilineSauga.objects.filter(imone=company)
        form.fields['position'].queryset = models.Position.objects.filter(company=company)
        form.fields['AsmeninesApsaugosPriemones'].queryset = company.AAP.all()
        form.fields['skyrius'].queryset = models.Skyrius.objects.filter(company=company)
        
        # Clear the AAP field so no items are pre-selected when loading the form
        # This prevents the field from showing currently assigned items
        if not self.request.POST:
            # Only clear on GET request (when loading the form), not on POST (when submitting)
            form.initial['AsmeninesApsaugosPriemones'] = []
        
        assigned_instructions = user_to_edit.instructions.all()  # Adjust if you use a different related name
        form.fields['instructions'].initial = [i.pk for i in assigned_instructions]
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_to_edit = self.get_object()
        context['assigned_instructions'] = [i.pk for i in user_to_edit.instructions.all()]
        context['priesgaisrines'] = [i.pk for i in user_to_edit.priesgaisrines.all()]
        context['civiline_sauga'] = [i.pk for i in user_to_edit.civiline_sauga.all()]
        context['mokymai'] = [i.pk for i in user_to_edit.mokymai.all()]
        context['kiti_dokumentai'] = [i.pk for i in user_to_edit.kiti_dokumentai.all()]
        context['AAP'] = [aap.pk for aap in user_to_edit.AsmeninesApsaugosPriemones.all()]
        # Repeat for other instruction types if needed
        return context

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
        AAP = form.cleaned_data.get('AsmeninesApsaugosPriemones')
        skyrius = form.cleaned_data.get('skyrius')
        kalba = form.cleaned_data.get('kalba')
        priesgaisrinesinstrukcijospasirasymai = models.PriesgaisriniuPasirasymas.objects.filter(user=user)
        civilinesaugapasirasymai = models.CivilineSaugaPasirasymas.objects.filter(user=user)
        mokymaipasirasymai = models.MokymuPasirasymas.objects.filter(user=user)
        kitidokumentaipasirasymai = models.KituDocPasirasymas.objects.filter(user=user)      
        existing_signs = models.UserInstructionSign.objects.filter(user=user)
        AAPPasirasymai = models.AAPPasirasymas.objects.filter(user=user)
        
        user.skyrius = skyrius
        user.kalba = kalba
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

        for AAP in AAP:
            existing_sign = AAPPasirasymai.filter(AAP=AAP).first()
            if existing_sign:
                if existing_sign.date_signed is not None:
                    existing_sign.next_sign = None
                    existing_sign.save()
                    models.AAPPasirasymas.objects.create(
                        user=user,
                        AAP=AAP,
                    )
                elif existing_sign.date_signed is None:
                    existing_sign.save()
            else:
                models.AAPPasirasymas.objects.create(
                    user=user,
                    AAP=AAP,
                )

        return super().form_valid(form)
    

class DokumentuListView(LoginRequiredMixin, generic.ListView):
    model = models.Instruction
    template_name = 'main/dokumentai_list.html'
    context_object_name = 'dokumentai'
    paginate_by = 10000

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['dokumentai'] = models.Instruction.objects.filter(company=self.request.user.company)
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


class AAPSignView(LoginRequiredMixin, generic.UpdateView):
    model = models.AAPPasirasymas
    form_class = forms.UserInstructionSignForm
    template_name = 'main/AAP_sign.html'

    def get_object(self, queryset=None):
        uuid = self.kwargs.get('uuid')
        return get_object_or_404(models.AAPPasirasymas, uuid=uuid)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['instruction'] = self.object.AAP
        context['pdf_url'] = self.object.AAP.pdf  # Correctly set the PDF URL
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.status = 1
        form.instance.date_signed = datetime.now()
        form.instance.next_sign = datetime.now() + timedelta(int(self.object.AAP.periodiskumas * 30))
        ip_address = self.get_client_ip(self.request)
        log_user_instruction_activity(self.request.user, self.object.AAP.pavadinimas, ip_address)
        
        return super().form_valid(form)

    def get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]  # Take the first IP in case of multiple proxies
        else:
            ip = request.META.get('REMOTE_ADDR')  # Fallback to REMOTE_ADDR
        
        return ip

    def get_success_url(self):
        return reverse_lazy('menu')


class AAPSignAjaxView(LoginRequiredMixin, generic.View):
    """AJAX view for signing AAP in modal"""
    
    def get(self, request, uuid):
        """Return AAP details as JSON"""
        try:
            aap_pasirasymas = get_object_or_404(models.AAPPasirasymas, uuid=uuid, user=request.user)
            aap = aap_pasirasymas.AAP
            
            data = {
                'success': True,
                'title': aap.pavadinimas,
                'pdf_url': aap.pdf.url if aap.pdf else None,
                'uuid': str(uuid),
            }
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    def post(self, request, uuid):
        """Handle AAP signing via AJAX"""
        try:
            aap_pasirasymas = get_object_or_404(models.AAPPasirasymas, uuid=uuid, user=request.user)
            
            # Update the signature
            aap_pasirasymas.status = 1
            aap_pasirasymas.date_signed = datetime.now()
            aap_pasirasymas.next_sign = datetime.now() + timedelta(int(aap_pasirasymas.AAP.periodiskumas * 30))
            aap_pasirasymas.save()
            
            # Log activity
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')
            
            log_user_instruction_activity(request.user, aap_pasirasymas.AAP.pavadinimas, ip_address)
            
            return JsonResponse({
                'success': True,
                'message': 'AAP pasirašyta sėkmingai'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)


def get_test_data(instruction):
    """Helper function to get test data for an instruction"""
    test = instruction.testas if hasattr(instruction, 'testas') and instruction.testas else None
    if not test:
        return None
    
    questions = []
    for klausimas in test.klausimai.all():
        answers = []
        for atsakymas in klausimas.atsakymai.all():
            answers.append({
                'id': atsakymas.id,
                'text': atsakymas.atsakymas,
                'is_correct': atsakymas.teisingas
            })
        questions.append({
            'id': klausimas.id,
            'question': klausimas.klausimas,
            'answers': answers
        })
    
    return {
        'id': test.id,
        'title': test.pavadinimas,
        'questions': questions
    }


class UserInstructionSignAjaxView(LoginRequiredMixin, generic.View):
    """AJAX view for signing User Instructions in modal"""
    
    def get(self, request, uuid):
        try:
            instruction_sign = get_object_or_404(models.UserInstructionSign, uuid=uuid, user=request.user)
            instruction = instruction_sign.instruction
            
            data = {
                'success': True,
                'title': instruction.name,
                'pdf_url': instruction.pdf.url if instruction.pdf else None,
                'uuid': str(uuid),
                'test': get_test_data(instruction)
            }
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    def post(self, request, uuid):
        try:
            import json
            instruction_sign = get_object_or_404(models.UserInstructionSign, uuid=uuid, user=request.user)
            instruction = instruction_sign.instruction
            
            # Validate test answers if test exists
            if instruction.testas:
                body = json.loads(request.body)
                test_answers = body.get('test_answers', {})
                
                for klausimas in instruction.testas.klausimai.all():
                    question_id = str(klausimas.id)
                    if question_id not in test_answers:
                        return JsonResponse({'success': False, 'error': 'Prašome atsakyti į visus klausimus'}, status=400)
                    
                    selected_answer_id = int(test_answers[question_id])
                    correct_answers = [a.id for a in klausimas.atsakymai.filter(teisingas=True)]
                    
                    if selected_answer_id not in correct_answers:
                        return JsonResponse({'success': False, 'error': 'Neteisingas atsakymas. Prašome bandyti dar kartą.'}, status=400)
            
            instruction_sign.status = 1
            instruction_sign.date_signed = datetime.now()
            instruction_sign.next_sign = datetime.now() + timedelta(int(instruction_sign.instruction.periodiskumas))
            instruction_sign.save()
            
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            ip_address = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
            
            log_user_instruction_activity(request.user, instruction_sign.instruction.name, ip_address)
            
            return JsonResponse({'success': True, 'message': 'Instrukcija pasirašyta sėkmingai'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)


class PriesgaisrinisSignAjaxView(LoginRequiredMixin, generic.View):
    """AJAX view for signing Priesgaisrinis instructions in modal"""
    
    def get(self, request, uuid):
        try:
            pasirasymas = get_object_or_404(models.PriesgaisriniuPasirasymas, uuid=uuid, user=request.user)
            instruction = pasirasymas.instruction
            
            data = {
                'success': True,
                'title': instruction.pavadinimas,
                'pdf_url': instruction.pdf.url if instruction.pdf else None,
                'uuid': str(uuid),
                'test': get_test_data(instruction)
            }
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    def post(self, request, uuid):
        try:
            pasirasymas = get_object_or_404(models.PriesgaisriniuPasirasymas, uuid=uuid, user=request.user)
            
            pasirasymas.status = 1
            pasirasymas.date_signed = datetime.now()
            pasirasymas.next_sign = datetime.now() + timedelta(int(pasirasymas.instruction.periodiskumas))
            pasirasymas.save()
            
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            ip_address = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
            
            log_user_instruction_activity(request.user, pasirasymas.instruction.pavadinimas, ip_address)
            
            return JsonResponse({'success': True, 'message': 'Priešgaisrinė instrukcija pasirašyta sėkmingai'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)


class CivilineSaugaSignAjaxView(LoginRequiredMixin, generic.View):
    """AJAX view for signing Civiline Sauga instructions in modal"""
    
    def get(self, request, uuid):
        try:
            pasirasymas = get_object_or_404(models.CivilineSaugaPasirasymas, uuid=uuid, user=request.user)
            instruction = pasirasymas.instruction
            
            data = {
                'success': True,
                'title': instruction.pavadinimas,
                'pdf_url': instruction.pdf.url if instruction.pdf else None,
                'uuid': str(uuid),
                'test': get_test_data(instruction)
            }
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    def post(self, request, uuid):
        try:
            pasirasymas = get_object_or_404(models.CivilineSaugaPasirasymas, uuid=uuid, user=request.user)
            
            pasirasymas.status = 1
            pasirasymas.date_signed = datetime.now()
            pasirasymas.next_sign = datetime.now() + timedelta(int(pasirasymas.instruction.periodiskumas))
            pasirasymas.save()
            
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            ip_address = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
            
            log_user_instruction_activity(request.user, pasirasymas.instruction.pavadinimas, ip_address)
            
            return JsonResponse({'success': True, 'message': 'Civilinės saugos instrukcija pasirašyta sėkmingai'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)


class MokymuSignAjaxView(LoginRequiredMixin, generic.View):
    """AJAX view for signing Mokymai in modal"""
    
    def get(self, request, uuid):
        try:
            pasirasymas = get_object_or_404(models.MokymuPasirasymas, uuid=uuid, user=request.user)
            mokymas = pasirasymas.instruction
            
            data = {
                'success': True,
                'title': mokymas.pavadinimas,
                'pdf_url': mokymas.pdf.url if mokymas.pdf else None,
                'uuid': str(uuid),
                'test': get_test_data(mokymas)
            }
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    def post(self, request, uuid):
        try:
            pasirasymas = get_object_or_404(models.MokymuPasirasymas, uuid=uuid, user=request.user)
            
            pasirasymas.status = 1
            pasirasymas.date_signed = datetime.now()
            pasirasymas.next_sign = datetime.now() + timedelta(int(pasirasymas.instruction.periodiskumas * 30))
            pasirasymas.save()
            
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            ip_address = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
            
            log_user_instruction_activity(request.user, pasirasymas.instruction.pavadinimas, ip_address)
            
            return JsonResponse({'success': True, 'message': 'Mokymas pasirašytas sėkmingai'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)


class KituDocSignAjaxView(LoginRequiredMixin, generic.View):
    """AJAX view for signing Kiti Dokumentai in modal"""
    
    def get(self, request, uuid):
        try:
            pasirasymas = get_object_or_404(models.KituDocPasirasymas, uuid=uuid, user=request.user)
            doc = pasirasymas.instruction
            
            data = {
                'success': True,
                'title': doc.pavadinimas,
                'pdf_url': doc.pdf.url if doc.pdf else None,
                'uuid': str(uuid),
                'test': get_test_data(doc)
            }
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    def post(self, request, uuid):
        try:
            pasirasymas = get_object_or_404(models.KituDocPasirasymas, uuid=uuid, user=request.user)
            
            pasirasymas.status = 1
            pasirasymas.date_signed = datetime.now()
            pasirasymas.next_sign = datetime.now() + timedelta(int(pasirasymas.instruction.periodiskumas * 30))
            pasirasymas.save()
            
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            ip_address = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
            
            log_user_instruction_activity(request.user, pasirasymas.instruction.pavadinimas, ip_address)
            
            return JsonResponse({'success': True, 'message': 'Dokumentas pasirašytas sėkmingai'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)


class AAPZurnalas(LoginRequiredMixin, generic.ListView):
    model = models.AAPPasirasymas
    template_name ='main/AAP_zurnalas.html'
    paginate_by = 10000

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
        
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date:
            queryset = queryset.filter(date_signed__gte=parse_date(start_date))
        if end_date:
            queryset = queryset.filter(date_signed__lte=parse_date(end_date))
        
        return queryset

    def generate_pdf(self, request):
        # Get the filtered queryset
        queryset = self.get_queryset()

        # Define the table structure
        table_headers = [
            'Vardas ir pavardė',
            'Gimimo data',
            'AAP pavadinimas',
            'Mato vnt.',
            'Kiekis',
            'Parašas',
            'Pasirašymo data',
            'Sekančio pasirašymo data',
        ]
        table_data = []

        for sign in queryset:
            row = [
                sign.user.get_full_name(),
                sign.user.date_of_birth,
                sign.AAP.get_full_name if sign.AAP.pavadinimas else 'N/A',
                sign.AAP.get_mato_vnt if sign.AAP.mato_vnt else 'N/A',
                1,
                'Pasirašyta' if sign.status == 1 else 'Nepasirašyta',
                sign.date_signed if sign.date_signed else 'N/A',
                sign.next_sign if sign.next_sign else 'N/A',
            ]
            table_data.append(row)

        context = {
            'title': 'ASMENINIŲ APSAUGOS PRIEMONIŲ IŠDAVIMO ŽINIARAŠTIS',
            'headers': table_headers,
            'data': table_data
        }
        # Render the PDF
        html_string = render_to_string('pdf_template.html', context)
        html = HTML(string=html_string)

        with tempfile.NamedTemporaryFile(delete=True) as output:
            html.write_pdf(target=output.name)
            output.seek(0)
            response = HttpResponse(output.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="AAP žiniaraštis.pdf"'
            return response

    def get(self, request, *args, **kwargs):
        if 'generate_pdf' in request.GET:
            return self.generate_pdf(request)
        return super().get(request, *args, **kwargs)

class InstructionAddAll(LoginRequiredMixin, generic.FormView):
    model = models.User
    form_class = forms.InstructionAddAllForm
    template_name = "main/InstructionAddAll.html"
    success_url = reverse_lazy('my_company_users')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        company = self.request.user.company
        selected_language = self.request.POST.get('kalba') or self.request.GET.get('kalba') or form.initial.get('kalba')
        # Filter instructions by selected language if provided
        if selected_language:
            form.fields['instructions'].queryset = models.Instruction.objects.filter(company=company, kalba=selected_language)
            form.fields['priesgaisrines'].queryset = models.PriesgiasrinesInstrukcijos.objects.filter(imone=company, kalba=selected_language)
            form.fields['mokymai'].queryset = models.Mokymai.objects.filter(imone=company, kalba=selected_language)
            form.fields['kiti_dokumentai'].queryset = models.KitiDokumentai.objects.filter(imone=company, kalba=selected_language)
            form.fields['civiline_sauga'].queryset = models.CivilineSauga.objects.filter(imone=company, kalba=selected_language)
        else:
            form.fields['instructions'].queryset = models.Instruction.objects.filter(company=company)
            form.fields['priesgaisrines'].queryset = models.PriesgiasrinesInstrukcijos.objects.filter(imone=company)
            form.fields['mokymai'].queryset = models.Mokymai.objects.filter(imone=company)
            form.fields['kiti_dokumentai'].queryset = models.KitiDokumentai.objects.filter(imone=company)
            form.fields['civiline_sauga'].queryset = models.CivilineSauga.objects.filter(imone=company)
        form.fields['position'].queryset = models.Position.objects.filter(company=company)
        form.fields['skyrius'].queryset = models.Skyrius.objects.filter(company=company)
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def create_instructions_for_user(self, user, form):
        """Assign selected instructions to a user, creating sign instances if needed."""
        instructions = form.cleaned_data.get('instructions')
        priesgaisrines = form.cleaned_data.get('priesgaisrines')
        civiline_sauga = form.cleaned_data.get('civiline_sauga')
        mokymai = form.cleaned_data.get('mokymai')
        kiti_dokumentai = form.cleaned_data.get('kiti_dokumentai')

        # Assign instructions (append, do not remove existing)
        if instructions:
            user.instructions.add(*instructions)
            for instruction in instructions:
                if not models.UserInstructionSign.objects.filter(user=user, instruction=instruction).exists():
                    models.UserInstructionSign.objects.create(user=user, instruction=instruction)

        if priesgaisrines:
            user.priesgaisrines.add(*priesgaisrines)
            for instruction in priesgaisrines:
                if not models.PriesgaisriniuPasirasymas.objects.filter(user=user, instruction=instruction).exists():
                    models.PriesgaisriniuPasirasymas.objects.create(user=user, instruction=instruction)

        if civiline_sauga:
            user.civiline_sauga.add(*civiline_sauga)
            for instruction in civiline_sauga:
                if not models.CivilineSaugaPasirasymas.objects.filter(user=user, instruction=instruction).exists():
                    models.CivilineSaugaPasirasymas.objects.create(user=user, instruction=instruction)

        if mokymai:
            user.mokymai.add(*mokymai)
            for instruction in mokymai:
                if not models.MokymuPasirasymas.objects.filter(user=user, instruction=instruction).exists():
                    models.MokymuPasirasymas.objects.create(user=user, instruction=instruction)

        if kiti_dokumentai:
            user.kiti_dokumentai.add(*kiti_dokumentai)
            for instruction in kiti_dokumentai:
                if not models.KituDocPasirasymas.objects.filter(user=user, instruction=instruction).exists():
                    models.KituDocPasirasymas.objects.create(user=user, instruction=instruction)



    def form_valid(self, form):
        with transaction.atomic():
            company = self.request.user.company
            kalba = form.cleaned_data.get('kalba')
            position = form.cleaned_data.get('position')
            skyrius = form.cleaned_data.get('skyrius')

            # Build user queryset based on filters
            user_list = models.User.objects.filter(company=company, is_active=True)
            if kalba:
                user_list = user_list.filter(kalba=kalba)
            if skyrius:
                user_list = user_list.filter(skyrius=skyrius)
            if position:
                user_list = user_list.filter(position=position)

            for user in user_list:
                self.create_instructions_for_user(user, form)

        return super().form_valid(form)


class AdminPriminimaiView(LoginRequiredMixin, generic.ListView):
    model = models.AdminPriminimas
    template_name = 'main/administracijos_priminimai.html'
    paginate_by = 10000
    context_object_name = 'admin_priminimai'

    def get_queryset(self):
        return models.AdminPriminimas.objects.filter(imone=self.request.user.company)


def get_instructions_by_language(request):
    kalba = request.GET.get('kalba')
    company = request.user.company
    data = {
        'instructions': [],
        'priesgaisrines': [],
        'mokymai': [],
        'kiti_dokumentai': [],
        'civiline_sauga': [],
    }
    if kalba:
        kalba = int(kalba)
        data['instructions'] = [
            {'id': i.id, 'name': i.name} for i in models.Instruction.objects.filter(company=company, kalba=int(kalba))
        ]
        data['priesgaisrines'] = [
            {'id': i.id, 'name': i.pavadinimas} for i in models.PriesgiasrinesInstrukcijos.objects.filter(imone=company, kalba=kalba)
        ]
        data['mokymai'] = [
            {'id': i.id, 'name': i.pavadinimas} for i in models.Mokymai.objects.filter(imone=company, kalba=kalba)
        ]
        data['kiti_dokumentai'] = [
            {'id': i.id, 'name': i.pavadinimas} for i in models.KitiDokumentai.objects.filter(imone=company, kalba=kalba)
        ]
        data['civiline_sauga'] = [
            {'id': i.id, 'name': i.pavadinimas} for i in models.CivilineSauga.objects.filter(imone=company, kalba=kalba)
        ]
    return JsonResponse(data)

class MenuBootstrapView(LoginRequiredMixin, generic.ListView):
    model = models.UserInstructionSign
    template_name = 'menu_bootstrap.html'
    paginate_by = 10000

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user, status=0)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # All pending instructions by type (status=0 means pending/unsigned)
        context['priesrines_instrukcijos'] = models.PriesgaisriniuPasirasymas.objects.filter(user=user, status=0)
        context['mokymo_instrukcijos'] = models.MokymuPasirasymas.objects.filter(user=user, status=0)
        context['kitu_doc'] = models.KituDocPasirasymas.objects.filter(user=user, status=0)
        context['civiline_sauga'] = models.CivilineSaugaPasirasymas.objects.filter(user=user, status=0)
        context['asmenines_apsaugos_priemones'] = models.AAPPasirasymas.objects.filter(user=user, status=0)
        
        # Calculate statistics for dashboard
        # Total pending instructions
        pending_count = (
            context['object_list'].count() +
            context['priesrines_instrukcijos'].count() +
            context['mokymo_instrukcijos'].count() +
            context['kitu_doc'].count() +
            context['civiline_sauga'].count() +
            context['asmenines_apsaugos_priemones'].count()
        )
        context['pending_instructions'] = pending_count
        
        # Total signed instructions (status=1 means signed)
        signed_count = (
            models.UserInstructionSign.objects.filter(user=user, status=1).count() +
            models.PriesgaisriniuPasirasymas.objects.filter(user=user, status=1).count() +
            models.MokymuPasirasymas.objects.filter(user=user, status=1).count() +
            models.KituDocPasirasymas.objects.filter(user=user, status=1).count() +
            models.CivilineSaugaPasirasymas.objects.filter(user=user, status=1).count() +
            models.AAPPasirasymas.objects.filter(user=user, status=1).count()
        )
        context['signed_instructions'] = signed_count
        
        # Total instructions (both signed and pending)
        context['total_instructions'] = pending_count + signed_count
        
        # Expired instructions (status=2 typically means expired/overdue)
        expired_count = (
            models.UserInstructionSign.objects.filter(user=user, status=2).count() +
            models.PriesgaisriniuPasirasymas.objects.filter(user=user, status=2).count() +
            models.MokymuPasirasymas.objects.filter(user=user, status=2).count() +
            models.KituDocPasirasymas.objects.filter(user=user, status=2).count() +
            models.CivilineSaugaPasirasymas.objects.filter(user=user, status=2).count() +
            models.AAPPasirasymas.objects.filter(user=user, status=2).count()
        )
        context['expired_instructions'] = expired_count
        
        context['user'] = user
        return context


# API views for document viewing in modal
class DocumentViewApiView(LoginRequiredMixin, View):
    """Base API view for document PDF retrieval"""
    
    def get_document_data(self, document, title_attr='name'):
        """Helper to extract document data"""
        if not document:
            return {'success': False, 'error': 'Document not found'}
        
        title = getattr(document, title_attr, 'Document')
        
        # Check if document has pdf attribute and file exists
        pdf_url = None
        if hasattr(document, 'pdf') and document.pdf:
            try:
                pdf_url = document.pdf.url
            except Exception as e:
                print(f"Error getting PDF URL: {e}")
        
        return {
            'success': True,
            'title': title,
            'pdf_url': pdf_url,
        }
    
    def get(self, request, uuid):
        raise NotImplementedError('Subclasses must implement get method')


class InstructionViewApiView(DocumentViewApiView):
    def get(self, request, uuid):
        instruction = get_object_or_404(models.Instruction, uuid=uuid)
        data = self.get_document_data(instruction, 'name')
        return JsonResponse(data)


class PriesgaisrinisViewApiView(DocumentViewApiView):
    def get(self, request, uuid):
        instruction = get_object_or_404(models.PriesgiasrinesInstrukcijos, uuid=uuid)
        data = self.get_document_data(instruction, 'pavadinimas')
        return JsonResponse(data)


class CivilineSaugaViewApiView(DocumentViewApiView):
    def get(self, request, uuid):
        instruction = get_object_or_404(models.CivilineSauga, uuid=uuid)
        data = self.get_document_data(instruction, 'pavadinimas')
        return JsonResponse(data)


class MokymasViewApiView(DocumentViewApiView):
    def get(self, request, uuid):
        instruction = get_object_or_404(models.Mokymai, uuid=uuid)
        data = self.get_document_data(instruction, 'pavadinimas')
        return JsonResponse(data)


class KituDocViewApiView(DocumentViewApiView):
    def get(self, request, uuid):
        instruction = get_object_or_404(models.KitiDokumentai, uuid=uuid)
        data = self.get_document_data(instruction, 'pavadinimas')
        return JsonResponse(data)
