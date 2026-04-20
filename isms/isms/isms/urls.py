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
    path("lista_ativos/", views.ReadAtivoView.as_view(), name="lista_ativos"),
    path("editar_ativo/<int:ativo_id>/", views.UpdateAtivoView.as_view(), name="editar_ativo"),
    path("deletar_ativo/<int:ativo_id>/", views.DeleteAtivoView.as_view(), name="deletar_ativo"),
    path("criacao_criterios_valoracao_ativos/", views.CriacaoCriteriosValoracaoAtivosView.as_view(), name="criacao_criterios_valoracao_ativos"),
    path("criacao_criterios_avaliacao_riscos/", views.CriacaoCriteriosAvaliacaoRiscosView.as_view(), name="criacao_criterios_avaliacao_riscos"),
    path("identificacao_riscos/", views.IdentificacaoRiscosView.as_view(), name="identificacao_riscos"),
    path("lista_riscos/", views.ReadRiscoView.as_view(), name="lista_riscos"),
    path("editar_risco/<int:risco_id>/", views.UpdateRiscoView.as_view(), name="editar_risco"),
    path("deletar_risco/<int:risco_id>/", views.DeleteRiscoView.as_view(), name="deletar_risco"),
    path("analise_riscos/", views.AnaliseRiscosView.as_view(), name="analise_riscos"),
    path("avaliacao_riscos/", views.AvaliacaoRiscoView.as_view(), name="avaliacao_riscos"),
    path("tratamento_riscos/", views.TratamentoRiscoView.as_view(), name="tratamento_riscos"),
    path("analise_valoracao_ativos/", views.AnaliseValoracaoAtivosView.as_view(), name="analise_valoracao_ativos"),
    path("gestao_incidentes/", views.GestaoIncidentesView.as_view(), name="gestao_incidentes"),
    path("cadastro_incidente/", views.CadastroIncidenteView.as_view(), name="cadastro_incidente"),
    path("visualizar_incidente/<int:incidente_id>/", views.VisualizarIncidenteView.as_view(), name="visualizar_incidente"),
    path("deletar_incidente/<int:incidente_id>/", views.DeleteIncidenteView.as_view(), name="deletar_incidente"),
    path("gerar_relatorio_incidente/<int:incidente_id>/", views.GerarRelatórioIncidenteView.as_view(), name="gerar_relatorio_incidente"),
    path("relatorio_incidente/<int:relatorio_id>/", views.RelatórioIncidenteView.as_view(), name="relatorio_incidente"),
    path("deteccao_ameaca/", views.DeteccaoAmeacaView.as_view(), name="deteccao_ameaca"),
    path("lista_ameacas/", views.ReadAmeacaView.as_view(), name="lista_ameacas"),
    path("editar_ameaca/<int:ameaca_id>/", views.UpdateAmeacaView.as_view(), name="editar_ameaca"),
    path("deletar_ameaca/<int:ameaca_id>/", views.DeleteAmeacaView.as_view(), name="deletar_ameaca"),
    path("gestao_vulnerabilidades/", views.VulnerabilidadeView.as_view(), name="gestao_vulnerabilidades"),
    path("lista_vulnerabilidades/", views.ReadVulnerabilidadeView.as_view(), name="lista_vulnerabilidades"),
    path("editar_vulnerabilidade/<int:vulnerabilidade_id>/", views.UpdateVulnerabilidadeView.as_view(), name="editar_vulnerabilidade"),
    path("deletar_vulnerabilidade/<int:vulnerabilidade_id>/", views.DeleteVulnerabilidadeView.as_view(), name="deletar_vulnerabilidade"),
    path("registro_auditoria/", views.RegistroAuditoriaView.as_view(), name="registro_auditoria"),
    path("lista_auditorias/", views.ReadAuditoriaView.as_view(), name="lista_auditorias"),
    path("editar_auditoria/<int:auditoria_id>/", views.UpdateAuditoriaView.as_view(), name="editar_auditoria"),
    path("deletar_auditoria/<int:auditoria_id>/", views.DeleteAuditoriaView.as_view(), name="deletar_auditoria"),
    path("cadastro_controle/", views.CadastroControleView.as_view(), name="cadastro_controle"),
    path("lista_controles/", views.ReadControleView.as_view(), name="lista_controles"),
    path("editar_controle/<int:controle_id>/", views.UpdateControleView.as_view(), name="editar_controle"),
    path("deletar_controle/<int:controle_id>/", views.DeleteControleView.as_view(), name="deletar_controle"),
]
