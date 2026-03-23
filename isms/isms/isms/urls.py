"""
URL configuration for isms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from ismsapp import views
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.HomeView.as_view(), name="home"),
    path("signup/", views.UserSignUpView.as_view(), name="signup"),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),
    path("profile/", views.UserProfileView.as_view(), name="profile"),
    path("profile/edit/", views.UserUpdateView.as_view(), name="edit_profile"),
    path("profile/delete/", views.UserDeleteView.as_view(), name="delete_account"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("password_change/", views.UserPasswordChange.as_view(), name="password_change"),
    path("password_change/done/", views.UserPasswordChangeDone.as_view(), name="password_change_done"),
    path("cadastro_categoria_ativo/", views.CadastroCategoriaAtivoView.as_view(), name="cadastro_categoria_ativo"),
    path("cadastro_ativo/", views.CadastroAtivoView.as_view(), name="cadastro_ativo"),
    path("criacao_criterios_valoracao_ativos/", views.CriacaoCriteriosValoracaoAtivosView.as_view(), name="criacao_criterios_valoracao_ativos"),
]
