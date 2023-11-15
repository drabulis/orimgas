from django.urls import path
from . import views


urlpatterns = [
    path('', views.UserMeniuView.as_view(), name='menu'),
    path('main/user_add/', views.AddUserView.as_view(), name='user_add'),
    path('main/user_instructions/', views.UserInstructionsView.as_view(), name='user_instructions'),
    path('main/user_edit/<int:pk>/', views.UserEditView.as_view(), name='user_edit'),
    path('main/user_detail/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
]
