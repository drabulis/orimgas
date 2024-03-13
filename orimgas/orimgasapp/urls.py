from django.urls import path
from django.contrib.auth.views import LoginView
from . import views


urlpatterns = [
    path('', views.UserMeniuView.as_view(), name='menu'),
    path('main/user_add/', views.AddUserView.as_view(), name='user_add'),
    path('main/user_instructions/', views.UserInstructionSignView.as_view(), name='user_instructions'),
    path('main/user_edit/<int:pk>/', views.UserEditView.as_view(), name='user_edit'),
    path('main/user_detail/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('main/my_company_users/', views.MyCompanyUsersView.as_view(), name='my_company_users'),
    path('main/user_instructions/<int:pk>_sign/', views.UserInstructionSignUpdateView.as_view(), name='user_instruction_detail'),
    path('main/kitu_doc_sign/<int:pk>/', views.KituDocSignView.as_view(), name='kitu_doc_sign'),
    path('main/mokymu_sign/<int:pk>/', views.MokymuSignView.as_view(), name='mokymu_sign'),
    path('main/priesgaisrinis_sign/<int:pk>/', views.PriesgaisrinioSignView.as_view(), name='priesgaisrinis_sign'),
    path('serve_pdf/<int:instruction_id>/', views.serve_pdf, name='serve_pdf'),
    path('main/supervisor_edit_user/<int:pk>/', views.SupervisorEditUserView.as_view(), name='supervisor_edit_user'),
    path('main/darbu_saugos_zurnalas', views.DarbuSaugosZurnalas.as_view(), name='darbu_saugos_zurnalas'),
    path('main/priesgaisrinės_saugos_zurnalas', views.PriesgaisrinesSaugosZurnalas.as_view(), name='priesgaisrinės_saugos_zurnalas'),
    path('main/mokymu_zurnalas', views.MokymuZurnalas.as_view(), name='mokymu_zurnalas'),
    path('main/kitu_doc_zurnalas', views.KituDocZurnalas.as_view(), name='kitu_doc_zurnalas'),
    path('main/sveikatos_tikrinimo_grafikas', views.SveikatosTikrinimoGrafikas.as_view(), name='sveikatos_tikrinimo_grafikas'),
    path('login/', LoginView.as_view(), name='login'),
]
