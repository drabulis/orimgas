from django.urls import path
from django.contrib.auth.views import LoginView
from django.views.i18n import set_language
from . import views


urlpatterns = [
    path('i18n/setlang/', set_language, name='set_language'),
    path('', views.UserMeniuView.as_view(), name='menu'),
    path('main/user_add/', views.AddUserView.as_view(), name='user_add'),
    path('main/user_instructions/', views.UserInstructionSignView.as_view(), name='user_instructions'),
    path('main/user_edit/<uuid:uuid>/', views.UserEditView.as_view(), name='user_edit'),
    path('main/user_detail/<uuid:uuid>/', views.UserDetailView.as_view(), name='user_detail'),
    path('main/my_company_users/', views.MyCompanyUsersView.as_view(), name='my_company_users'),
    path('main/user_instructions/<uuid:uuid>_sign/', views.UserInstructionSignUpdateView.as_view(), name='user_instruction_detail'),
    path('main/kitu_doc_sign/<uuid:uuid>/', views.KituDocSignView.as_view(), name='kitu_doc_sign'),
    path('main/mokymu_sign/<uuid:uuid>/', views.MokymuSignView.as_view(), name='mokymu_sign'),
    path('main/priesgaisrinis_sign/<uuid:uuid>/', views.PriesgaisrinioSignView.as_view(), name='priesgaisrinis_sign'),
    path('main/civiline_sauga_sign/<uuid:uuid>/', views.CivilineSaugaSignView.as_view(), name='civiline_sauga_sign'),
    path('serve_pdf/<int:instruction_id>/', views.serve_pdf, name='serve_pdf'),
    path('main/supervisor_edit_user/<uuid:uuid>/', views.SupervisorEditUserView.as_view(), name='supervisor_edit_user'),
    path('main/darbu_saugos_zurnalas', views.DarbuSaugosZurnalas.as_view(), name='darbu_saugos_zurnalas'),
    path('main/priesgaisrinės_saugos_zurnalas', views.PriesgaisrinesSaugosZurnalas.as_view(), name='priesgaisrinės_saugos_zurnalas'),
    path('main/civiline_saugos_zurnalas', views.CivilinesSaugosZurnalas.as_view(), name='civiline_sauga_zurnalas'),
    path('main/mokymu_zurnalas', views.MokymuZurnalas.as_view(), name='mokymu_zurnalas'),
    path('mokymai/<uuid:uuid>/pasirasymai/', views.MokymuPasirasymasList.as_view(), name='mokymu-pasirasymas-list'),
    path('main/kitu_doc_zurnalas', views.KituDocZurnalas.as_view(), name='kitu_doc_zurnalas'),
    path('main/sveikatos_tikrinimo_grafikas', views.SveikatosTikrinimoGrafikas.as_view(), name='sveikatos_tikrinimo_grafikas'),
    path('main/dokumentai_list', views.DokumentuListView.as_view(), name='dokumentai_list'),
    path('main/darbu_saugos/<uuid:uuid>/', views.UserInstructionReviewView.as_view(), name='darbu_sagos_detail'),
    path('main/priesgaisrinis/<uuid:uuid>/', views.PriesgaisrinioReviewView.as_view(), name='priesgaisrinio_detail'),
    path('main/civiline_sauga/<uuid:uuid>/', views.CivilineSaugaReviewView.as_view(), name='civiline_sauga_detail'),
    path('main/mokymai/<uuid:uuid>/', views.MokymuReviewView.as_view(), name='mokymu_detail'),
    path('main/kiti_dokumentai/<uuid:uuid>/', views.KituDocReviewView.as_view(), name='kiti_dokumentai_detail'),
    path('login/', LoginView.as_view(), name='login'),
]
