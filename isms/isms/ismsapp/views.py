from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.http.response import HttpResponseRedirect, JsonResponse
from django.urls.base import reverse_lazy, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from .forms import *
from .models import *

class HomeView(View):
    """Home page view - displays landing page.

    If user is already logged in, redirects to dashboard instead.
    """
    template_name = "ismsapp/home.html"

    def get(self, request, *args, **kwargs):
        # Redirect authenticated users to dashboard
        if request.user.is_authenticated:
            return redirect('dashboard')

        contexto = {}
        return render(request, self.template_name, contexto)


class UserSignUpView(View):
    """Sign up view for new users to create an account.

    This view handles both GET and POST requests:
    - GET: Displays the sign-up form with actor type options
    - POST: Processes form data, creates new user and user profile, redirects to login
    """
    form_class = SignUpForm
    template_name = "ismsapp/signup.html"

    def get(self, request, *args, **kwargs):
        formulario = self.form_class()
        contexto = {"formulario": formulario}
        return render(request, self.template_name, contexto)

    def post(self, request, *args, **kwargs):
        formulario = self.form_class(request.POST)
        if formulario.is_valid():
            usuario = formulario.save()
            return HttpResponseRedirect(reverse_lazy("login"))
        contexto = {"formulario": formulario}
        return render(request, self.template_name, contexto)


class UserLoginView(View):
    """Login view for existing users to access their accounts.

    This view handles both GET and POST requests:
    - GET: Displays the login form
    - POST: Authenticates user credentials and creates session, redirects to dashboard
    """
    form_class = LoginForm
    template_name = "ismsapp/login.html"

    def get(self, request, *args, **kwargs):
        formulario = self.form_class()
        contexto = {"formulario": formulario}
        return render(request, self.template_name, contexto)

    def post(self, request, *args, **kwargs):
        formulario = self.form_class(request.POST)
        if formulario.is_valid():
            email = formulario.cleaned_data.get("email")
            password = formulario.cleaned_data.get("password")

            # Authenticate by email: first get user by email, then check password
            try:
                usuario = User.objects.get(email=email)
                usuario = authenticate(request, username=usuario.username, password=password)
            except User.DoesNotExist:
                usuario = None

            if usuario is not None:
                login(request, usuario)
                return HttpResponseRedirect(reverse_lazy("dashboard"))
            else:
                contexto = {
                    "formulario": formulario,
                    "erro": "Email ou senha inválidos."
                }
                return render(request, self.template_name, contexto)

        contexto = {"formulario": formulario}
        return render(request, self.template_name, contexto)


class UserLogoutView(View):
    """Logout view for users to end their session.

    Displays a logout confirmation page that redirects to home after 5 seconds.
    """
    template_name = "ismsapp/logout.html"

    def get(self, request, *args, **kwargs):
        logout(request)
        return render(request, self.template_name)

class UserProfileView(View):
    """User profile view - displays user's profile information.

    Requires user to be logged in. Shows user details and actor type.
    """
    template_name = "ismsapp/profile.html"

    @method_decorator(login_required(login_url="login"))
    def get(self, request, *args, **kwargs):
        try:
            profile = request.user.profile
            actor_tipo = profile.get_actor_type_display()
        except UserProfile.DoesNotExist:
            actor_tipo = "Sem papel atribuído"

        contexto = {
            "usuario": request.user,
            "actor_tipo": actor_tipo,
        }
        return render(request, self.template_name, contexto)

class UserDeleteView(View):
    """User account deletion view - allows users to delete their account.

    Requires user to be logged in. Deletes user and associated profile, then redirects to home.
    """
    template_name = "ismsapp/delete_account.html"

    @method_decorator(login_required(login_url="login"))
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    @method_decorator(login_required(login_url="login"))
    def post(self, request, *args, **kwargs):
        user = request.user
        logout(request)  # Log out the user before deleting the account
        user.delete()  # This will also delete the associated UserProfile due to on_delete=models.CASCADE
        return redirect("home")

class UserUpdateView(View):
    """User profile update view - allows users to update their profile information.

    Requires user to be logged in. Allows updating email address.
    GET: Displays the update form with current user information
    POST: Processes form data and updates the user's email
    """
    form_class = UserProfileUpdateForm
    template_name = "ismsapp/edit_profile.html"

    @method_decorator(login_required(login_url="login"))
    def get(self, request, *args, **kwargs):
        formulario = self.form_class(initial={"email": request.user.email}, user=request.user)
        contexto = {
            "formulario": formulario,
            "usuario": request.user,
        }
        return render(request, self.template_name, contexto)

    @method_decorator(login_required(login_url="login"))
    def post(self, request, *args, **kwargs):
        formulario = self.form_class(request.POST, user=request.user)
        if formulario.is_valid():
            formulario.save()
            mensagem_sucesso = "Perfil atualizado com sucesso!"
            contexto = {
                "formulario": formulario,
                "usuario": request.user,
                "sucesso": mensagem_sucesso,
            }
            return render(request, self.template_name, contexto)
        else:
            contexto = {
                "formulario": formulario,
                "usuario": request.user,
            }
            return render(request, self.template_name, contexto)

class DashboardView(View):
    """Dashboard view - displays role-specific dashboard for authenticated users.

    Requires user to be logged in. Shows user information and actor type.

    Each actor type can have different dashboard content based on their role in the system.

    """
    template_name = "ismsapp/dashboard.html"

    #Creating "White lists" for each functionality/ user case

    #cadastro de categoria de ativos
    cadastra_categoria_de_ativos = [
        UserProfile.Actor.SISTEMA_ADMIN,
        UserProfile.Actor.AUDITOR
    ]

    #cadastro de ativos
    cadastra_ativos = [
        UserProfile.Actor.SISTEMA_ADMIN,
        UserProfile.Actor.AUDITOR
    ]

    #criacao de criterios de valoracao dos ativos
    cria_criterios_de_valoracao_dos_ativos = [
        UserProfile.Actor.SISTEMA_ADMIN,
        UserProfile.Actor.AUDITOR
    ]

    #analise da valoracao dos ativos
    analisa_valoracao_dos_ativos = [
        UserProfile.Actor.AUDITOR,
        UserProfile.Actor.ANALISTA
    ]

    #criacao de criterios para avaliacao dos riscos
    cria_criterios_para_avaliacao_dos_riscos = [
        UserProfile.Actor.SISTEMA_ADMIN,
        UserProfile.Actor.AUDITOR
    ]

    #identificacao de riscos
    identifica_riscos = [
        UserProfile.Actor.AUDITOR,
        UserProfile.Actor.ANALISTA
    ]

    #analise de riscos
    analisa_riscos = [
        UserProfile.Actor.ANALISTA
    ]

    #avaliacao de riscos
    avalia_riscos = [
        UserProfile.Actor.AUDITOR
    ]

    #tratamento de riscos
    trata_riscos = [
        UserProfile.Actor.AUDITOR,
        UserProfile.Actor.ANALISTA
    ]

    #gestao de incidentes de seguranca
    gestao_de_incidentes_de_seguranca = [
        UserProfile.Actor.AUDITOR,
        UserProfile.Actor.ANALISTA
    ]

    #deteccao de ameacas
    deteccao_de_ameacas = [
        UserProfile.Actor.AUDITOR,
        UserProfile.Actor.ANALISTA
    ]

    #monitoramento continuo
    monitoramento_continuo = [
        UserProfile.Actor.ANALISTA
    ]

    #gestao de vulnerabilidades
    gestao_de_vulnerabilidade = [
        UserProfile.Actor.AUDITOR,
        UserProfile.Actor.ANALISTA
    ]

    #auditoria e revisao
    auditoria_e_revisao = [
        UserProfile.Actor.AUDITOR
    ]

    #gestao de auditorias internas e externas
    gestao_de_auditorias = [
        UserProfile.Actor.AUDITOR
    ]

    #gestao de controles de seguranca
    gestao_de_controles = [
        UserProfile.Actor.SISTEMA_ADMIN,
        UserProfile.Actor.AUDITOR
    ]

    @method_decorator(login_required(login_url="login"))
    def get(self, request, *args, **kwargs):
        try:
            profile = request.user.profile
            actor_tipo = profile.get_actor_type_display()
            actor_type = profile.actor_type
        except UserProfile.DoesNotExist:
            actor_tipo = "Sem papel atribuído"
            actor_type = None

        # Check if user can access cadastro de categorias de ativos
        pode_cadastrar_categorias_de_ativos = actor_type in self.cadastra_categoria_de_ativos if actor_type else False
        pode_cadastrar_ativos = actor_type in self.cadastra_ativos if actor_type else False
        pode_criar_criterios_de_valoracao_dos_ativos = actor_type in self.cria_criterios_de_valoracao_dos_ativos if actor_type else False
        pode_analisar_valoracao_dos_ativos = actor_type in self.analisa_valoracao_dos_ativos if actor_type else False
        pode_criar_criterios_para_avaliacao_dos_riscos = actor_type in self.cria_criterios_para_avaliacao_dos_riscos if actor_type else False
        pode_identificar_riscos = actor_type in self.identifica_riscos if actor_type else False
        pode_analisar_riscos = actor_type in self.analisa_riscos if actor_type else False
        pode_avaliar_riscos = actor_type in self.avalia_riscos if actor_type else False
        pode_tratar_riscos = actor_type in self.trata_riscos if actor_type else False
        pode_gestionar_incidentes_de_seguranca = actor_type in self.gestao_de_incidentes_de_seguranca if actor_type else False
        pode_detectar_ameacas = actor_type in self.deteccao_de_ameacas if actor_type else False
        pode_monitorar_continuamente = actor_type in self.monitoramento_continuo if actor_type else False
        pode_gerenciar_vulnerabilidades = actor_type in self.gestao_de_vulnerabilidade if actor_type else False
        pode_auditar_e_revisar = actor_type in self.auditoria_e_revisao if actor_type else False
        pode_gerenciar_auditorias = actor_type in self.gestao_de_auditorias if actor_type else False
        pode_registrar_auditorias = actor_type in self.gestao_de_auditorias if actor_type else False
        pode_gerenciar_controles = actor_type in self.gestao_de_controles if actor_type else False

        # Get monitoring data for UC-12
        from .models import Incidente, Risco, Vulnerabilidade
        from datetime import timedelta
        from django.utils import timezone
        from django.db.models import Count, Q

        # 1. RISK TREATMENT STATUS - Count treatments by type
        tratamentos_por_tipo = Tratamento.objects.values('tipo_tratamento').annotate(count=Count('id')).order_by('tipo_tratamento')
        tratamento_status = {
            'aceitar': 0,
            'mitigar': 0,
            'evitar': 0,
            'compartilhar': 0
        }
        for t in tratamentos_por_tipo:
            tratamento_status[t['tipo_tratamento']] = t['count']

        # 2. INCIDENT TREND - Get incidents by status (last 30 days and all time)
        dias_atras_30 = timezone.now() - timedelta(days=30)

        # Total counts by status (all time)
        incidente_status_total = Incidente.objects.filter(status__isnull=False).values('status').annotate(count=Count('id')).order_by('status')

        # Last 30 days by status
        incidente_status_30dias = Incidente.objects.filter(
            data_registro__gte=dias_atras_30,
            status__isnull=False
        ).values('status').annotate(count=Count('id')).order_by('status')

        # Format for template
        incident_trend = {
            'registrado': {'total': 0, 'dias_30': 0},
            'em_investigacao': {'total': 0, 'dias_30': 0},
            'resolvido': {'total': 0, 'dias_30': 0}
        }

        for item in incidente_status_total:
            if item['status'] in incident_trend:
                incident_trend[item['status']]['total'] = item['count']

        for item in incidente_status_30dias:
            if item['status'] in incident_trend:
                incident_trend[item['status']]['dias_30'] = item['count']

        # 3. ARTIFACT COMPLIANCE SUMMARY - Vulnerabilities count
        total_vulnerabilidades = Vulnerabilidade.objects.count()
        vulnerability_summary = {
            'total': total_vulnerabilidades
        }

        # 4. HIGH-PRIORITY RISKS - Top 5 risks by inherent risk value
        riscos_prioritarios = Risco.objects.filter(
            Q(valor_risco_inerente__isnull=False) | Q(nivel_inerente__isnull=False)
        ).select_related('ativo', 'nivel_inerente').order_by('-valor_risco_inerente')[:5]

        contexto = {
            "usuario": request.user,
            "actor_tipo": actor_tipo,
            "pode_cadastrar_categorias_de_ativos": pode_cadastrar_categorias_de_ativos,
            "pode_cadastrar_ativos": pode_cadastrar_ativos,
            "pode_criar_criterios_de_valoracao_dos_ativos": pode_criar_criterios_de_valoracao_dos_ativos,
            "pode_analisar_valoracao_dos_ativos": pode_analisar_valoracao_dos_ativos,
            "pode_criar_criterios_para_avaliacao_dos_riscos": pode_criar_criterios_para_avaliacao_dos_riscos,
            "pode_identificar_riscos": pode_identificar_riscos,
            "pode_analisar_riscos": pode_analisar_riscos,
            "pode_avaliar_riscos": pode_avaliar_riscos,
            "pode_tratar_riscos": pode_tratar_riscos,
            "pode_gestionar_incidentes_de_seguranca": pode_gestionar_incidentes_de_seguranca,
            "pode_detectar_ameacas": pode_detectar_ameacas,
            "pode_monitorar_continuamente": pode_monitorar_continuamente,
            "pode_gerenciar_vulnerabilidades": pode_gerenciar_vulnerabilidades,
            "pode_auditar_e_revisar": pode_auditar_e_revisar,
            "pode_gerenciar_auditorias": pode_gerenciar_auditorias,
            "pode_registrar_auditorias": pode_registrar_auditorias,
            "pode_gerenciar_controles": pode_gerenciar_controles,
            # New monitoring data - UC-12 Enhanced
            "tratamento_status": tratamento_status,
            "incident_trend": incident_trend,
            "vulnerability_summary": vulnerability_summary,
            "riscos_prioritarios": riscos_prioritarios,
        }

        return render(request, self.template_name, contexto)

class UserPasswordChange(View):
    """User password change view - allows users to change their password.

    Requires user to be logged in. Validates current password and new password confirmation.
    GET: Displays the password change form
    POST: Processes form data and updates the user's password
    """
    form_class = UserPasswordChangeForm
    template_name = "ismsapp/password_change.html"

    @method_decorator(login_required(login_url="login"))
    def get(self, request, *args, **kwargs):
        formulario = self.form_class(user=request.user)
        contexto = {
            "formulario": formulario,
        }
        return render(request, self.template_name, contexto)

    @method_decorator(login_required(login_url="login"))
    def post(self, request, *args, **kwargs):
        formulario = self.form_class(request.POST, user=request.user)
        if formulario.is_valid():
            formulario.save()
            return HttpResponseRedirect(reverse_lazy("password_change_done"))
        else:
            contexto = {
                "formulario": formulario,
            }
            return render(request, self.template_name, contexto)

class UserPasswordChangeDone(View):
    """User password change done view - displays success message after password change.

    Requires user to be logged in. Shows confirmation that password has been changed.
    """
    template_name = "ismsapp/password_change_done.html"

    @method_decorator(login_required(login_url="login"))
    def get(self, request, *args, **kwargs):
        contexto = {}
        return render(request, self.template_name, contexto)

class CadastroCategoriaAtivoView(View):
    """View para cadastro de categoria de ativo.

    Esta view permite que os usuários cadastrados como Administrador do sistema
    ou Auditor de Segurança da Informação cadastrem novas categorias de ativos.
    Requer que o usuário esteja autenticado e tenha permissão apropriada.

    Usuarios autorizados:
    - Administrador do sistema (SISTEMA_ADMIN)
    - Auditor de Segurança (AUDITOR)
    """
    form_class = CadastroCategoriaAtivoForm
    template_name = "ismsapp/cadastro_categoria_ativo.html"

    def _check_permission(self, user):
        """Check if user has permission to register asset categories.

        Only Administrador do sistema and Auditor de Segurança are allowed
        to register asset categories.
        """
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        # Only System Admin and Information Security Auditor can register categories
        allowed_actors = [
            UserProfile.Actor.SISTEMA_ADMIN,
            UserProfile.Actor.AUDITOR
        ]
        return user_profile.actor_type in allowed_actors

    @method_decorator(login_required(login_url="login"))
    def get(self, request, *args, **kwargs):
        if not self._check_permission(request.user):
            return redirect('dashboard')

        form = self.form_class()
        contexto = {'form': form}
        return render(request, self.template_name, contexto)

    @method_decorator(login_required(login_url="login"))
    def post(self, request, *args, **kwargs):
        if not self._check_permission(request.user):
            return redirect('dashboard')

        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')

        contexto = {'form': form}
        return render(request, self.template_name, contexto)

#Assets CRUD
class CadastroAtivoView(View):
    """View para cadastro de ativo.

    Esta view permite que os usuários cadastrados como Administrador do sistema
    ou Auditor de Segurança da Informação cadastrem novos ativos.
    Requer que o usuário esteja autenticado e tenha permissão apropriada.

    Usuarios autorizados:
    - Administrador do sistema (SISTEMA_ADMIN)
    - Auditor de Segurança (AUDITOR)
    """
    form_class = CadastroAtivoForm
    template_name = "ismsapp/cadastro_ativo.html"

    def _check_permission(self, user):
        """Check if user has permission to register assets.

        Only Administrador do sistema and Auditor de Segurança are allowed
        to register assets.
        """
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        # Only System Admin and Information Security Auditor can register assets
        allowed_actors = [
            UserProfile.Actor.SISTEMA_ADMIN,
            UserProfile.Actor.AUDITOR
        ]
        return user_profile.actor_type in allowed_actors

    @method_decorator(login_required(login_url="login"))
    def get(self, request, *args, **kwargs):
        if not self._check_permission(request.user):
            return redirect('dashboard')

        form = self.form_class()
        contexto = {'form': form}
        return render(request, self.template_name, contexto)

    @method_decorator(login_required(login_url="login"))
    def post(self, request, *args, **kwargs):
        if not self._check_permission(request.user):
            return redirect('dashboard')

        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')

        contexto = {'form': form}
        return render(request, self.template_name, contexto)

class ReadAtivoView(View):
    """View para leitura/listagem de ativos.

    Esta view exibe uma lista de todos os ativos cadastrados no sistema
    com opções para editar ou deletar cada um.
    Requer que o usuário esteja autenticado e tenha permissão apropriada.

    Usuarios autorizados:
    - Administrador do sistema (SISTEMA_ADMIN)
    - Auditor de Segurança (AUDITOR)
    - Analista de Segurança (ANALISTA)
    """
    template_name = "ismsapp/lista_ativos.html"

    def _check_permission(self, user):
        """Check if user has permission to view assets.

        Only Administrador do sistema, Auditor de Segurança, and Analista
        are allowed to view assets.
        """
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        # System Admin, Information Security Auditor, and Security Analyst can view assets
        allowed_actors = [
            UserProfile.Actor.SISTEMA_ADMIN,
            UserProfile.Actor.AUDITOR,
            UserProfile.Actor.ANALISTA
        ]
        return user_profile.actor_type in allowed_actors

    @method_decorator(login_required(login_url="login"))
    def get(self, request, *args, **kwargs):
        if not self._check_permission(request.user):
            return redirect('dashboard')

        from .models import Ativo
        from django.db.models import Q

        search_query = request.GET.get('search', '').strip()
        ativos = Ativo.objects.all().order_by('nome')

        if search_query:
            ativos = ativos.filter(
                Q(nome__icontains=search_query) |
                Q(categoria__nome__icontains=search_query)
            )

        # Check edit/delete permissions
        user_profile = getattr(request.user, 'profile', None)
        pode_editar_deletar = user_profile and user_profile.actor_type in [
            UserProfile.Actor.SISTEMA_ADMIN,
            UserProfile.Actor.AUDITOR
        ]

        contexto = {
            'ativos': ativos,
            'pode_editar_deletar': pode_editar_deletar,
            'search_query': search_query,
        }
        return render(request, self.template_name, contexto)


class UpdateAtivoView(View):
    """View para edição/atualização de ativo.

    Esta view permite que os usuários cadastrados como Administrador do sistema
    ou Auditor de Segurança da Informação editem ativos existentes.
    Requer que o usuário esteja autenticado e tenha permissão apropriada.

    Usuarios autorizados:
    - Administrador do sistema (SISTEMA_ADMIN)
    - Auditor de Segurança (AUDITOR)
    """
    form_class = CadastroAtivoForm
    template_name = "ismsapp/editar_ativo.html"

    def _check_permission(self, user):
        """Check if user has permission to update assets.

        Only Administrador do sistema and Auditor de Segurança are allowed
        to update assets.
        """
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        # Only System Admin and Information Security Auditor can update assets
        allowed_actors = [
            UserProfile.Actor.SISTEMA_ADMIN,
            UserProfile.Actor.AUDITOR
        ]
        return user_profile.actor_type in allowed_actors

    @method_decorator(login_required(login_url="login"))
    def get(self, request, ativo_id=None, *args, **kwargs):
        if not self._check_permission(request.user):
            return redirect('dashboard')

        from .models import Ativo

        if not ativo_id:
            return redirect('lista_ativos')

        try:
            ativo = Ativo.objects.get(id=ativo_id)
        except Ativo.DoesNotExist:
            return redirect('lista_ativos')

        form = self.form_class(instance=ativo)
        contexto = {
            'form': form,
            'ativo': ativo,
            'ativo_id': ativo_id,
        }
        return render(request, self.template_name, contexto)

    @method_decorator(login_required(login_url="login"))
    def post(self, request, ativo_id=None, *args, **kwargs):
        if not self._check_permission(request.user):
            return redirect('dashboard')

        from .models import Ativo

        if not ativo_id:
            return redirect('lista_ativos')

        try:
            ativo = Ativo.objects.get(id=ativo_id)
        except Ativo.DoesNotExist:
            return redirect('lista_ativos')

        form = self.form_class(request.POST, instance=ativo)
        if form.is_valid():
            form.save()
            return redirect('lista_ativos')

        contexto = {
            'form': form,
            'ativo': ativo,
            'ativo_id': ativo_id,
        }
        return render(request, self.template_name, contexto)


class DeleteAtivoView(View):
    """View para deletar ativo.

    Esta view permite que os usuários cadastrados como Administrador do sistema
    ou Auditor de Segurança da Informação deletem ativos existentes.
    Requer que o usuário esteja autenticado e tenha permissão apropriada.

    Usuarios autorizados:
    - Administrador do sistema (SISTEMA_ADMIN)
    - Auditor de Segurança (AUDITOR)
    """
    template_name = "ismsapp/deletar_ativo.html"

    def _check_permission(self, user):
        """Check if user has permission to delete assets.

        Only Administrador do sistema and Auditor de Segurança are allowed
        to delete assets.
        """
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        # Only System Admin and Information Security Auditor can delete assets
        allowed_actors = [
            UserProfile.Actor.SISTEMA_ADMIN,
            UserProfile.Actor.AUDITOR
        ]
        return user_profile.actor_type in allowed_actors

    @method_decorator(login_required(login_url="login"))
    def get(self, request, ativo_id=None, *args, **kwargs):
        if not self._check_permission(request.user):
            return redirect('dashboard')

        from .models import Ativo

        if not ativo_id:
            return redirect('lista_ativos')

        try:
            ativo = Ativo.objects.get(id=ativo_id)
        except Ativo.DoesNotExist:
            return redirect('lista_ativos')

        contexto = {
            'ativo': ativo,
            'ativo_id': ativo_id,
        }
        return render(request, self.template_name, contexto)

    @method_decorator(login_required(login_url="login"))
    def post(self, request, ativo_id=None, *args, **kwargs):
        if not self._check_permission(request.user):
            return redirect('dashboard')

        from .models import Ativo

        if not ativo_id:
            return redirect('lista_ativos')

        try:
            ativo = Ativo.objects.get(id=ativo_id)
            ativo.delete()
            return redirect('lista_ativos')
        except Ativo.DoesNotExist:
            return redirect('lista_ativos')

class CriacaoCriteriosValoracaoAtivosView(View):
    """View para criação de critérios de valoração dos ativos.

    Esta view permite que os usuários cadastrados como Administrador do sistema
    ou Auditor de Segurança da Informação definam os pesos CIDP (Confidencialidade,
    Integridade, Disponibilidade, Privacidade) para um ativo específico.
    Requer que o usuário esteja autenticado e tenha permissão apropriada.

    Usuarios autorizados:
    - Administrador do sistema (SISTEMA_ADMIN)
    - Auditor de Segurança (AUDITOR)
    """
    form_class = CriacaoCriteriosValoracaoAtivosForm
    template_name = "ismsapp/criacao_criterios_valoracao_ativos.html"

    def _check_permission(self, user):
        """Check if user has permission to create asset valuation criteria.

        Only Administrador do sistema and Auditor de Segurança are allowed.
        """
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        # Unified valuation page is available for admin, auditor and analyst roles.
        allowed_actors = [
            UserProfile.Actor.SISTEMA_ADMIN,
            UserProfile.Actor.AUDITOR,
            UserProfile.Actor.ANALISTA
        ]
        return user_profile.actor_type in allowed_actors

    def _calcular_valor_ativo(self, ativo):
        """Calculate the asset valuation score based on CIDP ratings."""
        cidp_values = [
            ativo.confidencialidade,
            ativo.integridade,
            ativo.disponibilidade,
            ativo.privacidade,
        ]

        rated_values = [v for v in cidp_values if v > 0]

        if not rated_values:
            return {
                'score': 0,
                'score_texto': '0.0',
                'nivel_risco': 'SEM AVALIAÇÃO',
                'classe_risco': 'sem-risco'
            }

        score = round(sum(rated_values) / len(rated_values), 1)

        if score >= 4.5:
            nivel_risco = 'MUITO ALTO'
            classe_risco = 'muito-alto'
        elif score >= 3.5:
            nivel_risco = 'ALTO'
            classe_risco = 'alto'
        elif score >= 2.5:
            nivel_risco = 'MÉDIO'
            classe_risco = 'medio'
        elif score >= 1.5:
            nivel_risco = 'BAIXO'
            classe_risco = 'baixo'
        else:
            nivel_risco = 'MUITO BAIXO'
            classe_risco = 'muito-baixo'

        return {
            'score': score,
            'score_texto': f'{score:.1f}',
            'nivel_risco': nivel_risco,
            'classe_risco': classe_risco
        }

    @method_decorator(login_required(login_url="login"))
    def get(self, request, ativo_id=None, *args, **kwargs):
        if not self._check_permission(request.user):
            return redirect('dashboard')

        from .models import Ativo

        # Get all assets for selection
        ativos = Ativo.objects.all()

        # If ativo_id is provided (path or query string), load that specific asset
        ativo = None
        form = None
        valuation_data = None
        selected_ativo_id = ativo_id or request.GET.get('ativo_id')
        if selected_ativo_id:
            try:
                ativo = Ativo.objects.get(id=selected_ativo_id)
                form = self.form_class(instance=ativo)
                valuation_data = self._calcular_valor_ativo(ativo)
            except Ativo.DoesNotExist:
                pass

        if not form:
            form = self.form_class()

        contexto = {
            'form': form,
            'ativos': ativos,
            'ativo_selecionado': ativo,
            'valuation_data': valuation_data,
        }
        return render(request, self.template_name, contexto)

    @method_decorator(login_required(login_url="login"))
    def post(self, request, *args, **kwargs):
        if not self._check_permission(request.user):
            return redirect('dashboard')

        from .models import Ativo

        ativo_id = request.POST.get('ativo_id')
        if not ativo_id:
            # If no ativo selected, show form again with error
            form = self.form_class()
            ativos = Ativo.objects.all()
            contexto = {
                'form': form,
                'ativos': ativos,
                'erro': 'Por favor, selecione um ativo.',
            }
            return render(request, self.template_name, contexto)

        try:
            ativo = Ativo.objects.get(id=ativo_id)
        except Ativo.DoesNotExist:
            form = self.form_class()
            ativos = Ativo.objects.all()
            contexto = {
                'form': form,
                'ativos': ativos,
                'erro': 'Ativo não encontrado.',
            }
            return render(request, self.template_name, contexto)

        form = self.form_class(request.POST, instance=ativo)
        if form.is_valid():
            ativo = form.save()
            messages.success(request, f'Valoração do ativo "{ativo.nome}" salva com sucesso!')

            ativos = Ativo.objects.all()
            contexto = {
                'form': self.form_class(instance=ativo),
                'ativos': ativos,
                'ativo_selecionado': ativo,
                'valuation_data': self._calcular_valor_ativo(ativo),
            }
            return render(request, self.template_name, contexto)

        ativos = Ativo.objects.all()
        contexto = {
            'form': form,
            'ativos': ativos,
            'ativo_selecionado': ativo,
            'valuation_data': self._calcular_valor_ativo(ativo),
        }
        return render(request, self.template_name, contexto)

class AnaliseValoracaoAtivosView(View):
    """Compatibility wrapper: analysis URL now uses the unified valuation page."""

    def dispatch(self, request, *args, **kwargs):
        unified_view = CriacaoCriteriosValoracaoAtivosView.as_view()
        return unified_view(request, *args, **kwargs)

class CriacaoCriteriosAvaliacaoRiscosView(View):
    """View para criação de critérios para avaliação dos riscos.

    Esta view permite que os usuários cadastrados como Administrador do sistema
    ou Auditor de Segurança da Informação definam os critérios de avaliação dos riscos
    (escalas de probabilidade, consequência e apetite ao risco organizacional).
    Requer que o usuário esteja autenticado e tenha permissão apropriada.

    Usuarios autorizados:
    - Administrador do sistema (SISTEMA_ADMIN)
    - Auditor de Segurança (AUDITOR)
    """
    form_class = CriacaoCriteriosAvaliacaoRiscosForm
    template_name = "ismsapp/criacao_criterios_avaliacao_riscos.html"

    def _check_permission(self, user):
        """Check if user has permission to create risk evaluation criteria."""
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        # Only System Admin and Information Security Auditor can create criteria
        allowed_actors = [
            UserProfile.Actor.SISTEMA_ADMIN,
            UserProfile.Actor.AUDITOR
        ]
        return user_profile.actor_type in allowed_actors

    def _generate_risk_matrix(self, criterio):
        """Generate a 5x5 risk matrix based on probability and consequence scales."""
        matrix = []
        for consequence in range(5, 0, -1):  # 5 to 1 (top to bottom)
            row = []
            for probability in range(1, 6):  # 1 to 5 (left to right)
                risk_score = probability * consequence  # Simple risk score calculation
                # Determine risk level based on score
                if risk_score <= 5:
                    risk_level = "Baixo"
                elif risk_score <= 10:
                    risk_level = "Moderado"
                elif risk_score <= 15:
                    risk_level = "Alto"
                else:
                    risk_level = "Crítico"
                row.append({
                    'score': risk_score,
                    'level': risk_level,
                    'probability': probability,
                    'consequence': consequence
                })
            matrix.append(row)
        return matrix

    @method_decorator(login_required(login_url="login"))
    def get(self, request, *args, **kwargs):
        if not self._check_permission(request.user):
            messages.error(request, "Você não tem permissão para acessar esta página.")
            return redirect('dashboard')

        # Get existing criteria if any
        criterio = CriterioAvaliacaoRisco.objects.first()
        if criterio:
            form = self.form_class(instance=criterio)
            risk_matrix = self._generate_risk_matrix(criterio)
            is_edit = True
        else:
            form = self.form_class()
            risk_matrix = self._generate_risk_matrix(None)
            is_edit = False

        contexto = {
            'form': form,
            'risk_matrix': risk_matrix,
            'is_edit': is_edit
        }
        return render(request, self.template_name, contexto)

    @method_decorator(login_required(login_url="login"))
    def post(self, request, *args, **kwargs):
        if not self._check_permission(request.user):
            messages.error(request, "Você não tem permissão para acessar esta página.")
            return redirect('dashboard')

        from .models import Probabilidade, Consequencia, Nivel
        from decimal import Decimal

        # Get existing criteria if any
        criterio = CriterioAvaliacaoRisco.objects.first()

        # Create form with POST data
        if criterio:
            form = self.form_class(request.POST, instance=criterio)
        else:
            form = self.form_class(request.POST)

        if form.is_valid():
            # Save the criteria
            criterio = form.save()

            # Create Probabilidade records for each level
            prob_data = [
                (Probabilidade.Categoria.MUITO_BAIXA, 1, form.cleaned_data.get('escala_probabilidade_1', 'Muito Baixo')),
                (Probabilidade.Categoria.BAIXA, 2, form.cleaned_data.get('escala_probabilidade_2', 'Baixo')),
                (Probabilidade.Categoria.MEDIA, 3, form.cleaned_data.get('escala_probabilidade_3', 'Médio')),
                (Probabilidade.Categoria.ALTA, 4, form.cleaned_data.get('escala_probabilidade_4', 'Alto')),
                (Probabilidade.Categoria.MUITO_ALTA, 5, form.cleaned_data.get('escala_probabilidade_5', 'Muito Alto')),
            ]

            for categoria, peso, descricao in prob_data:
                Probabilidade.objects.update_or_create(
                    categoria=categoria,
                    defaults={
                        'peso': Decimal(str(peso)),
                        'descricao': descricao
                    }
                )

            # Create Consequencia records for each level
            cons_data = [
                (Consequencia.Categoria.MUITO_BAIXO, 1, form.cleaned_data.get('escala_consequencia_1', 'Muito Baixo')),
                (Consequencia.Categoria.BAIXO, 2, form.cleaned_data.get('escala_consequencia_2', 'Baixo')),
                (Consequencia.Categoria.MEDIO, 3, form.cleaned_data.get('escala_consequencia_3', 'Médio')),
                (Consequencia.Categoria.ALTO, 4, form.cleaned_data.get('escala_consequencia_4', 'Alto')),
                (Consequencia.Categoria.MUITO_ALTO, 5, form.cleaned_data.get('escala_consequencia_5', 'Muito Alto')),
            ]

            for categoria, peso, descricao in cons_data:
                Consequencia.objects.update_or_create(
                    categoria=categoria,
                    defaults={
                        'peso': Decimal(str(peso)),
                        'descricao': descricao
                    }
                )

            # Create Nivel records for INERENTE and RESIDUAL types
            nivel_data = [
                ('Baixo', Decimal('5.00')),
                ('Moderado', Decimal('10.00')),
                ('Alto', Decimal('15.00')),
                ('Crítico', Decimal('25.00')),
            ]

            for tipo in [Nivel.Tipo.INERENTE, Nivel.Tipo.RESIDUAL]:
                for categoria, peso in nivel_data:
                    Nivel.objects.update_or_create(
                        categoria=categoria,
                        tipo=tipo,
                        defaults={'peso': peso}
                    )
            return redirect('dashboard')

        # Regenerate matrix for display
        criterio = CriterioAvaliacaoRisco.objects.first()
        if criterio:
            risk_matrix = self._generate_risk_matrix(criterio)
        else:
            risk_matrix = self._generate_risk_matrix(None)

        contexto = {
            'form': form,
            'risk_matrix': risk_matrix,
            'is_edit': criterio is not None
        }
        return render(request, self.template_name, contexto)

class IdentificacaoRiscosView(View):
    """View para identificação de riscos.

    Esta view permite que os usuários cadastrados como Auditor de Segurança da Informação
    ou Analista de Segurança da Informação identifiquem riscos relacionados a um ativo específico.
    Requer que o usuário esteja autenticado e tenha permissão apropriada.

    Usuarios autorizados:
    - Auditor de Segurança (AUDITOR)
    - Analista de Segurança (ANALISTA)
    """
    form_class = IdentificacaoRiscosForm
    template_name = "ismsapp/identificacao_riscos.html"

    def _check_permission(self, user):
        """Check if user has permission to identify risks."""
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        # Only Information Security Auditor and Analyst can identify risks
        allowed_actors = [
            UserProfile.Actor.AUDITOR,
            UserProfile.Actor.ANALISTA
        ]
        return user_profile.actor_type in allowed_actors

    @method_decorator(login_required(login_url="login"))
    def get(self, request, *args, **kwargs):
        if not self._check_permission(request.user):
            messages.error(request, "Você não tem permissão para acessar esta página.")
            return redirect('dashboard')

        from .models import Ativo

        # Get all assets for selection
        ativos = Ativo.objects.all()

        contexto = {
            'form': self.form_class(),
            'ativos': ativos,
            'risks_identificados': None,
            'ativo_selecionado': None,
        }
        return render(request, self.template_name, contexto)

    @method_decorator(login_required(login_url="login"))
    def post(self, request, *args, **kwargs):
        if not self._check_permission(request.user):
            messages.error(request, "Você não tem permissão para acessar esta página.")
            return redirect('dashboard')

        from .models import Ativo, Risco

        form = self.form_class(request.POST)
        if form.is_valid():
            # Extract form data
            nome = form.cleaned_data.get('nome')
            descricao = form.cleaned_data.get('descricao')
            ativo = form.cleaned_data.get('ativo')

            # Create Risco object with separate fields
            risco = Risco(
                nome=nome,
                descricao=descricao,
                ativo=ativo,
                tipo=Risco.Tipo.INERENTE  # Default to INERENTE as starting point
            )
            risco.save()

            return redirect('dashboard')

        # If form is invalid, re-render the template with errors
        ativos = Ativo.objects.all()
        contexto = {
            'form': form,
            'ativos': ativos,
            'ativo_selecionado': form.data.get('ativo'),
        }
        return render(request, self.template_name, contexto)

# Risk CRUD

# Risk CRUD

class ReadRiscoView(View):
    """View para listagem/leitura de riscos.

    Esta view exibe uma lista de todos os riscos cadastrados no sistema
    com opções para editar ou deletar cada um.
    Requer que o usuário esteja autenticado e tenha permissão apropriada.

    Usuarios autorizados:
    - Auditor de Segurança (AUDITOR)
    - Analista de Segurança (ANALISTA)
    """
    template_name = "ismsapp/lista_riscos.html"

    def _check_permission(self, user):
        """Check if user has permission to view risks."""
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        allowed_actors = [
            UserProfile.Actor.AUDITOR,
            UserProfile.Actor.ANALISTA
        ]
        return user_profile.actor_type in allowed_actors

    def _check_edit_permission(self, user):
        """Check if user has permission to edit/delete risks (more restrictive)."""
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        allowed_actors = [
            UserProfile.Actor.AUDITOR,
            UserProfile.Actor.ANALISTA
        ]
        return user_profile.actor_type in allowed_actors

    @method_decorator(login_required(login_url="login"))
    def get(self, request, *args, **kwargs):
        if not self._check_permission(request.user):
            return redirect('dashboard')

        from .models import Risco
        from django.db.models import Q

        search_query = request.GET.get('search', '').strip()
        riscos = Risco.objects.all().order_by('-id')

        if search_query:
            riscos = riscos.filter(
                Q(nome__icontains=search_query) |
                Q(descricao__icontains=search_query) |
                Q(ativo__nome__icontains=search_query)
            )

        pode_editar_deletar = self._check_edit_permission(request.user)

        contexto = {
            'riscos': riscos,
            'pode_editar_deletar': pode_editar_deletar,
            'search_query': search_query,
        }
        return render(request, self.template_name, contexto)


class UpdateRiscoView(View):
    """View para edição/atualização de risco.

    Esta view permite que os usuários cadastrados como Auditor ou Analista de Segurança
    editem riscos existentes.
    Requer que o usuário esteja autenticado e tenha permissão apropriada.

    Usuarios autorizados:
    - Auditor de Segurança (AUDITOR)
    - Analista de Segurança (ANALISTA)
    """
    form_class = AtualizacaoRiscosForm
    template_name = "ismsapp/editar_risco.html"

    def _check_permission(self, user):
        """Check if user has permission to update risks."""
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        allowed_actors = [
            UserProfile.Actor.AUDITOR,
            UserProfile.Actor.ANALISTA
        ]
        return user_profile.actor_type in allowed_actors

    @method_decorator(login_required(login_url="login"))
    def get(self, request, risco_id=None, *args, **kwargs):
        if not self._check_permission(request.user):
            return redirect('dashboard')

        from .models import Risco

        if not risco_id:
            return redirect('lista_riscos')

        try:
            risco = Risco.objects.get(id=risco_id)
        except Risco.DoesNotExist:
            return redirect('lista_riscos')

        form = self.form_class(initial={
            'nome': risco.nome,
            'descricao': risco.descricao,
            'ativo': risco.ativo
        })
        contexto = {
            'form': form,
            'risco': risco,
            'risco_id': risco_id,
        }
        return render(request, self.template_name, contexto)

    @method_decorator(login_required(login_url="login"))
    def post(self, request, risco_id=None, *args, **kwargs):
        if not self._check_permission(request.user):
            return redirect('dashboard')

        from .models import Risco

        if not risco_id:
            return redirect('lista_riscos')

        try:
            risco = Risco.objects.get(id=risco_id)
        except Risco.DoesNotExist:
            return redirect('lista_riscos')

        form = self.form_class(request.POST)
        if form.is_valid():
            risco.nome = form.cleaned_data.get('nome')
            risco.descricao = form.cleaned_data.get('descricao')
            risco.ativo = form.cleaned_data.get('ativo')
            risco.save()
            return redirect('lista_riscos')

        contexto = {
            'form': form,
            'risco': risco,
            'risco_id': risco_id,
        }
        return render(request, self.template_name, contexto)


class DeleteRiscoView(View):
    """View para deletar risco.

    Esta view permite que os usuários cadastrados como Auditor ou Analista de Segurança
    deletem riscos existentes.
    Requer que o usuário esteja autenticado e tenha permissão apropriada.

    Usuarios autorizados:
    - Auditor de Segurança (AUDITOR)
    - Analista de Segurança (ANALISTA)
    """
    template_name = "ismsapp/deletar_risco.html"

    def _check_permission(self, user):
        """Check if user has permission to delete risks."""
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        allowed_actors = [
            UserProfile.Actor.AUDITOR,
            UserProfile.Actor.ANALISTA
        ]
        return user_profile.actor_type in allowed_actors

    @method_decorator(login_required(login_url="login"))
    def get(self, request, risco_id=None, *args, **kwargs):
        if not self._check_permission(request.user):
            return redirect('dashboard')

        from .models import Risco

        if not risco_id:
            return redirect('lista_riscos')

        try:
            risco = Risco.objects.get(id=risco_id)
        except Risco.DoesNotExist:
            return redirect('lista_riscos')

        contexto = {
            'risco': risco,
            'risco_id': risco_id,
        }
        return render(request, self.template_name, contexto)

    @method_decorator(login_required(login_url="login"))
    def post(self, request, risco_id=None, *args, **kwargs):
        if not self._check_permission(request.user):
            return redirect('dashboard')

        from .models import Risco

        if not risco_id:
            return redirect('lista_riscos')

        try:
            risco = Risco.objects.get(id=risco_id)
            risco.delete()
            return redirect('lista_riscos')
        except Risco.DoesNotExist:
            return redirect('lista_riscos')

class AnaliseRiscosView(View):
    """View for analyzing identified risks.

    This view allows authorized users to analyze risks by assessing their
    probability and consequence levels, and viewing the resulting risk values
    on a risk matrix.

    Authorized users:
    - Information Security Auditor (AUDITOR)
    - Information Security Analyst (ANALISTA)
    """
    template_name = "ismsapp/analise_riscos.html"

    def _check_permission(self, user):
        """Check if user has permission to analyze risks."""
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        allowed_actors = [
            UserProfile.Actor.AUDITOR,
            UserProfile.Actor.ANALISTA
        ]
        return user_profile.actor_type in allowed_actors

    @method_decorator(login_required(login_url="login"))
    def get(self, request, *args, **kwargs):
        if not self._check_permission(request.user):
            messages.error(request, "Você não tem permissão para acessar esta página.")
            return redirect('dashboard')

        from .models import Risco

        # Get all risks for analysis
        riscos = Risco.objects.all()

        contexto = {
            'riscos': riscos,
        }
        return render(request, self.template_name, contexto)

    @method_decorator(login_required(login_url="login"))
    def post(self, request, *args, **kwargs):
        if not self._check_permission(request.user):
            messages.error(request, "Você não tem permissão para acessar esta página.")
            return redirect('dashboard')

        from .models import Risco, Probabilidade, Consequencia, Nivel
        from decimal import Decimal

        risco_id = request.POST.get('risco_id')
        probabilidade_value = request.POST.get('probabilidade')
        consequencia_value = request.POST.get('consequencia')

        if risco_id and probabilidade_value and consequencia_value:
            try:
                risco = Risco.objects.get(id=risco_id)

                # Convert string values to integers
                prob_int = int(probabilidade_value)
                cons_int = int(consequencia_value)

                # Map numeric scale (1-5) to categoria values
                prob_categoria_map = {
                    1: Probabilidade.Categoria.MUITO_BAIXA,
                    2: Probabilidade.Categoria.BAIXA,
                    3: Probabilidade.Categoria.MEDIA,
                    4: Probabilidade.Categoria.ALTA,
                    5: Probabilidade.Categoria.MUITO_ALTA,
                }

                cons_categoria_map = {
                    1: Consequencia.Categoria.MUITO_BAIXO,
                    2: Consequencia.Categoria.BAIXO,
                    3: Consequencia.Categoria.MEDIO,
                    4: Consequencia.Categoria.ALTO,
                    5: Consequencia.Categoria.MUITO_ALTO,
                }

                # Get Probabilidade and Consequencia objects
                prob_categoria = prob_categoria_map.get(prob_int)
                cons_categoria = cons_categoria_map.get(cons_int)

                if not prob_categoria or not cons_categoria:
                    messages.error(request, "Valores de probabilidade ou consequência inválidos.")
                    riscos = Risco.objects.all()
                    return render(request, self.template_name, {'riscos': riscos})

                try:
                    # Use .value to convert enum to string
                    probabilidade_obj = Probabilidade.objects.get(categoria=prob_categoria.value)
                except Probabilidade.DoesNotExist:
                    messages.error(request, "Probabilidade não encontrada na base de dados. Verifique se a categoria foi criada.")
                    riscos = Risco.objects.all()
                    return render(request, self.template_name, {'riscos': riscos})

                try:
                    # Use .value to convert enum to string
                    consequencia_obj = Consequencia.objects.get(categoria=cons_categoria.value)
                except Consequencia.DoesNotExist:
                    messages.error(request, "Consequência não encontrada na base de dados. Verifique se a categoria foi criada.")
                    riscos = Risco.objects.all()
                    return render(request, self.template_name, {'riscos': riscos})

                # Calculate risk level (probability * consequence)
                risk_score = prob_int * cons_int

                # Look up Nivel by peso (weight) and tipo (type)
                nivel_obj = None
                try:
                    # Try to find nivel where peso is closest to risk_score
                    nivel_candidates = Nivel.objects.filter(
                        tipo=Nivel.Tipo.INERENTE
                    ).order_by('peso')

                    if nivel_candidates.exists():
                        # Find the nivel with peso that matches or is closest to risk_score
                        for nivel in nivel_candidates:
                            if float(nivel.peso) >= risk_score:
                                nivel_obj = nivel
                                break
                        # If none found with peso >= risk_score, use the highest one
                        if nivel_obj is None:
                            nivel_obj = nivel_candidates.last()

                except Nivel.DoesNotExist:
                    nivel_obj = None

                # Update risk with inherent assessment
                risco.probabilidade_inerente = probabilidade_obj
                risco.consequencia_inerente = consequencia_obj
                if nivel_obj:
                    risco.nivel_inerente = nivel_obj

                # Save the calculated inherent risk value
                risco.valor_risco_inerente = Decimal(str(risk_score))

                risco.save()

                return redirect('dashboard')

            except Risco.DoesNotExist:
                messages.error(request, "Risco não encontrado.")
            except Exception as e:
                messages.error(request, f"Erro ao salvar análise: {str(e)}")

        riscos = Risco.objects.all()
        contexto = {
            'riscos': riscos,
            'erro': 'Por favor, preencha todos os campos.',
        }
        return render(request, self.template_name, contexto)

class AvaliacaoRiscoView(View):
    """View for evaluating analyzed risks against acceptance criteria.

    This view allows authorized users to review analyzed risks, compare them
    with organizational risk appetite criteria, and decide whether to accept
    the risk or send it for treatment.

    The view implements the UC-08 use case (Avaliação de Riscos) which:
    1. Displays analyzed risks with their calculated risk levels
    2. Compares the risk with defined acceptance criteria
    3. Indicates whether the risk should be treated or accepted
    4. Records the evaluation decision

    Authorized users:
    - Information Security Auditor (AUDITOR)

    Main flow:
    - User accesses analyzed risks
    - System presents the calculated risk level
    - System compares risiko with acceptance criteria
    - System recommends acceptance or treatment
    - User confirms the decision
    - System records the decision
    """

    template_name = "ismsapp/avaliacao_riscos.html"
    form_class = AvaliacaoRiscosForm

    def _check_permission(self, user):
        """Check if user has permission to evaluate risks.

        Only Information Security Auditor (AUDITOR) is allowed
        to evaluate risks against acceptance criteria.
        """
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        allowed_actors = [
            UserProfile.Actor.AUDITOR
        ]
        return user_profile.actor_type in allowed_actors

    def _get_acceptance_level(self, criterio):
        """Determine the acceptable risk level based on risk appetite.

        Maps the organization's risk appetite to a numeric threshold.
        Risks below this threshold are acceptable without treatment.

        Risk Appetite Levels:
        - BAIXO (Low): 8 points or below
        - MODERADO (Moderate): 12 points or below
        - ALTO (High): 16 points or below
        """
        appetite_thresholds = {
            CriterioAvaliacaoRisco.ApetiteRisco.BAIXO: 8,
            CriterioAvaliacaoRisco.ApetiteRisco.MODERADO: 12,
            CriterioAvaliacaoRisco.ApetiteRisco.ALTO: 16,
        }
        return appetite_thresholds.get(criterio.apetite_risco, 12)

    def _is_risk_acceptable(self, risk_value, acceptance_level):
        """Determine if a risk value is acceptable based on criteria.

        A risk is acceptable if its numeric value is less than or equal
        to the organization's defined acceptance level.
        """
        try:
            return float(risk_value) <= acceptance_level
        except (TypeError, ValueError):
            return False

    def _get_suggestions_for_risk(self, risk_level):
        """Get treatment suggestions based on risk level.

        Maps risk levels to appropriate treatment strategies based on the
        organizational risk appetite criteria shown in the reference image:

        - Baixo (Low): Tolerável - Aceitar
        - Médio (Medium): Tolerável com monitoring - Aceitar
        - Alto (High): Não tolerável - Tratar (modify, avoid, share)
        - Crítico (Critical): Não tolerável - Tratar (modify, avoid, share)

        Returns a dict with suggestions for the risk level.
        """
        risk_level_lower = risk_level.lower() if risk_level else ""

        suggestions = {
            'nivel_risco': risk_level,
            'recomendacoes': [],
            'cor_categoria': 'neutral',
            'icone': 'info'
        }

        if 'baixo' in risk_level_lower:
            suggestions.update({
                'cor_categoria': 'baixo',
                'icone': 'check-circle',
                'recomendacoes': [
                    {
                        'titulo': 'Aceitar',
                        'descricao': 'Risco tolerável, sem necessidade de acompanhamento especial.',
                        'tipo': 'aceitar'
                    }
                ]
            })
        elif 'médio' in risk_level_lower or 'medio' in risk_level_lower:
            suggestions.update({
                'cor_categoria': 'medio',
                'icone': 'alert-circle',
                'recomendacoes': [
                    {
                        'titulo': 'Aceitar',
                        'descricao': 'Risco tolerável, porém com chances razoáveis de impacto moderado. Monitorar sem urgência.',
                        'tipo': 'aceitar'
                    }
                ]
            })
        elif 'alto' in risk_level_lower:
            suggestions.update({
                'cor_categoria': 'alto',
                'icone': 'alert-triangle',
                'recomendacoes': [
                    {
                        'titulo': 'Tratar',
                        'descricao': 'Risco não tolerável. Deve ser monitorado continuamente e controles implementados imediatamente.',
                        'tipo': 'tratar',
                        'acoes': ['Modificar ou mitigar', 'Evitar a atividade', 'Compartilhar ou transferir']
                    }
                ]
            })
        elif 'crítico' in risk_level_lower or 'critico' in risk_level_lower:
            suggestions.update({
                'cor_categoria': 'critico',
                'icone': 'alert-triangle',
                'recomendacoes': [
                    {
                        'titulo': 'Tratar',
                        'descricao': 'Risco crítico - impacto e probabilidade ultrapassam os critérios definidos. Ação imediata necessária.',
                        'tipo': 'tratar',
                        'acoes': ['Modificar ou mitigar urgentemente', 'Evitar a atividade', 'Compartilhar ou transferir']
                    }
                ]
            })

        return suggestions

    @method_decorator(login_required(login_url="login"))
    def get(self, request, *args, **kwargs):
        """Display evaluated risks or a specific risk for evaluation."""

        if not self._check_permission(request.user):
            messages.error(request, "Você não tem permissão para acessar esta página.")
            return redirect('dashboard')

        from .models import Risco, CriterioAvaliacaoRisco

        # Get the organization's risk acceptance criteria
        try:
            criterio_avaliacao = CriterioAvaliacaoRisco.objects.first()
        except CriterioAvaliacaoRisco.DoesNotExist:
            criterio_avaliacao = None
            messages.warning(request, "Nenhum critério de avaliação de risco foi definido. Configure os critérios antes de avaliar riscos.")

        acceptance_level = self._get_acceptance_level(criterio_avaliacao) if criterio_avaliacao else 12

        # Get analyzed risks (those with a calculated inherent risk value)
        riscos_analisados = Risco.objects.exclude(
            valor_risco_inerente__isnull=True
        ).select_related(
            'ativo',
            'nivel_inerente',
            'consequencia_inerente',
            'probabilidade_inerente'
        ).prefetch_related('tratamentos')

        # Get risco_id from query parameter
        risco_id = request.GET.get('risco_id')

        # If a specific risk ID was provided, get that risk
        risco_selecionado = None
        if risco_id:
            try:
                risco_selecionado = riscos_analisados.get(id=risco_id)
            except Risco.DoesNotExist:
                messages.error(request, "Risco não encontrado ou não foi analisado ainda.")
                risco_selecionado = None

        # Prepare risk evaluation data for display
        riscos_para_apresentacao = []
        for risco in riscos_analisados:
            is_acceptable = self._is_risk_acceptable(
                risco.valor_risco_inerente,
                acceptance_level
            )

            risco_data = {
                'risco': risco,
                'valor_risco': float(risco.valor_risco_inerente) if risco.valor_risco_inerente else 0,
                'nivel_risco': risco.nivel_inerente.categoria if risco.nivel_inerente else 'Não Definido',
                'aceitavel': is_acceptable,
                'necessita_tratamento': not is_acceptable,
                'ativo_nome': risco.ativo.nome if risco.ativo else 'Desconhecido',
                'descricao': risco.descricao,
            }
            riscos_para_apresentacao.append(risco_data)

        # Get suggestions for selected risk
        sugestoes = None
        if risco_selecionado and risco_selecionado.nivel_inerente:
            sugestoes = self._get_suggestions_for_risk(risco_selecionado.nivel_inerente.categoria)

        contexto = {
            'riscos': riscos_para_apresentacao,
            'risco_selecionado': risco_selecionado,
            'criterio_avaliacao': criterio_avaliacao,
            'apetite_risco': criterio_avaliacao.get_apetite_risco_display() if criterio_avaliacao else 'Não Definido',
            'acceptance_level': acceptance_level,
            'sugestoes': sugestoes,
        }

        return render(request, self.template_name, contexto)

    @method_decorator(login_required(login_url="login"))
    def post(self, request, *args, **kwargs):
        """Process risk evaluation decision (accept or treat)."""

        if not self._check_permission(request.user):
            messages.error(request, "Você não tem permissão para acessar esta página.")
            return redirect('dashboard')

        from .models import Risco, Tratamento, CriterioAvaliacaoRisco
        from django.utils import timezone

        risco_id = request.POST.get('risco_id')
        decisao = request.POST.get('decisao')
        observacoes = request.POST.get('observacoes', '')

        if not risco_id or not decisao:
            messages.error(request, "Por favor, selecione um risco e uma decisão.")
            return redirect('avaliacao_riscos')

        try:
            risco = Risco.objects.get(id=risco_id)

            if decisao not in ['aceitar', 'tratar']:
                messages.error(request, "Decisão inválida.")
                return redirect('avaliacao_riscos')

            # Process the evaluation decision
            if decisao == 'tratar':
                # Redirect to treatment creation view with the risk ID
                return HttpResponseRedirect(f"{reverse('tratamento_riscos')}?risco_id={risco.id}")

            elif decisao == 'aceitar':
                # Create an "Aceitar" treatment for this risk
                from .models import Tratamento

                tratamento_aceitar = Tratamento.objects.create(
                    nome=f"Aceitação de Risco - {risco.nome}",
                    tipo_tratamento=Tratamento.TipoTratamento.ACEITAR,
                    descricao=f"Risco {risco.nome} foi aceito pela organização sem necessidade de tratamento adicional.",
                    aceito=True,
                    reducao_probabilidade=0,
                    reducao_impacto=0,
                )

                # Link the acceptance treatment to the risk
                risco.tratamentos.add(tratamento_aceitar)

                return redirect('dashboard')

        except Risco.DoesNotExist:
            messages.error(request, "Risco não encontrado.")
            return redirect('avaliacao_riscos')
        except Exception as e:
            messages.error(request, f"Erro ao processar decisão: {str(e)}")
            return redirect('avaliacao_riscos')

class TratamentoRiscoView(View):
    """View for creating and managing risk treatment plans.

    This view allows authorized users to define treatment strategies for risks,
    including mitigation actions, responsible parties, deadlines, and expected
    risk reduction. The view implements UC-09 (Tratamento de Riscos).

    The flow is:
    1. User accesses a risk requiring treatment
    2. User selects treatment strategy (mitigar, evitar, compartilhar, aceitar)
    3. User defines mitigation actions and controls
    4. User registers responsible party and deadline
    5. System recalculates residual risk level
    6. System shows updated risk matrix position
    7. System registers the treatment plan

    Authorized users:
    - Information Security Auditor (AUDITOR)
    - Information Security Analyst (ANALISTA)
    """

    template_name = "ismsapp/tratamento_riscos.html"
    form_class = TratamentoRiscoForm

    def _check_permission(self, user):
        """Check if user has permission to create risk treatments."""
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        allowed_actors = [
            UserProfile.Actor.AUDITOR,
            UserProfile.Actor.ANALISTA
        ]
        return user_profile.actor_type in allowed_actors

    def _calculate_residual_risk(self, risk, reducao_prob, reducao_impacto):
        """Calculate residual risk level after treatment.

        Uses the reduction percentages to estimate new probability and consequence.
        """
        from .models import Probabilidade, Consequencia, Nivel
        from decimal import Decimal

        if not risk.probabilidade_inerente or not risk.consequencia_inerente:
            return None, None, None

        # Get current weights
        prob_weight = float(risk.probabilidade_inerente.peso)
        cons_weight = float(risk.consequencia_inerente.peso)

        # Calculate reduced weights
        new_prob_weight = prob_weight * (1 - (reducao_prob / 100))
        new_cons_weight = cons_weight * (1 - (reducao_impacto / 100))

        # Calculate new risk value
        new_risk_value = new_prob_weight * new_cons_weight

        # Find corresponding Nivel
        nivel_candidates = Nivel.objects.filter(
            tipo=Nivel.Tipo.RESIDUAL
        ).order_by('peso')

        nivel_residual = None
        if nivel_candidates.exists():
            for nivel in nivel_candidates:
                if float(nivel.peso) >= new_risk_value:
                    nivel_residual = nivel
                    break
            if nivel_residual is None:
                nivel_residual = nivel_candidates.last()

        return Decimal(str(new_risk_value)), nivel_residual, {
            'prob_original': prob_weight,
            'prob_nova': new_prob_weight,
            'cons_original': cons_weight,
            'cons_nova': new_cons_weight,
        }

    def _get_suggestions_for_risk(self, risk_level):
        """Get treatment suggestions based on risk level.

        Maps risk levels to appropriate treatment strategies based on the
        organizational risk appetite criteria:

        - Baixo (Low): Tolerável - Aceitar
        - Médio (Medium): Tolerável com monitoring - Aceitar
        - Alto (High): Não tolerável - Tratar (modify, avoid, share)
        - Crítico (Critical): Não tolerável - Tratar (modify, avoid, share)

        Returns a dict with suggestions for the risk level.
        """
        if not risk_level:
            return None

        risk_level_lower = str(risk_level).strip().lower()

        suggestions = {
            'nivel_risco': risk_level,
            'recomendacoes': [],
            'cor_categoria': 'neutral',
            'icone': 'info'
        }

        if 'baixo' in risk_level_lower:
            suggestions = {
                'nivel_risco': risk_level,
                'cor_categoria': 'baixo',
                'icone': 'check-circle',
                'recomendacoes': [
                    {
                        'titulo': 'Aceitar',
                        'descricao': 'Risco tolerável, sem necessidade de acompanhamento especial.',
                        'tipo': 'aceitar'
                    }
                ]
            }
        elif 'moderado' in risk_level_lower or 'médio' in risk_level_lower:
            suggestions = {
                'nivel_risco': risk_level,
                'cor_categoria': 'medio',
                'icone': 'alert-circle',
                'recomendacoes': [
                    {
                        'titulo': 'Aceitar',
                        'descricao': 'Risco tolerável, porém com chances razoáveis de impacto moderado. Monitorar sem urgência.',
                        'tipo': 'aceitar'
                    }
                ]
            }
        elif 'alto' in risk_level_lower:
            suggestions = {
                'nivel_risco': risk_level,
                'cor_categoria': 'alto',
                'icone': 'alert-triangle',
                'recomendacoes': [
                    {
                        'titulo': 'Tratar',
                        'descricao': 'Risco não tolerável. Deve ser monitorado continuamente e controles implementados imediatamente.',
                        'tipo': 'tratar',
                        'acoes': ['Modificar ou mitigar', 'Evitar a atividade', 'Compartilhar ou transferir']
                    }
                ]
            }
        elif 'crítico' in risk_level_lower or 'critico' in risk_level_lower:
            suggestions = {
                'nivel_risco': risk_level,
                'cor_categoria': 'critico',
                'icone': 'alert-triangle',
                'recomendacoes': [
                    {
                        'titulo': 'Tratar',
                        'descricao': 'Risco crítico - impacto e probabilidade ultrapassam os critérios definidos. Ação imediata necessária.',
                        'tipo': 'tratar',
                        'acoes': ['Modificar ou mitigar urgentemente', 'Evitar a atividade', 'Compartilhar ou transferir']
                    }
                ]
            }

        return suggestions if suggestions['recomendacoes'] else None

    def _calculate_control_reductions(self, controles):
        """Calculate expected risk reductions based on control types (HYBRID APPROACH).

        Based on the control categories and their effectiveness:
        - Preventivo: Reduces Probability (X), no impact on Consequence (-)
        - Detectivo: Reduces both Probability (X) and Consequence (X)
        - Corretivo/Contingência: Reduces Consequence (X), no impact on Probability (-)

        Returns a dict with:
        - prob_reduction: Expected probability reduction %
        - impact_reduction: Expected consequence/impact reduction %
        - breakdown: List of controls and their effects
        """
        from .models import CategoriaControle

        prob_reduction = 0
        impact_reduction = 0
        breakdown = []

        if not controles:
            return {
                'prob_reduction': prob_reduction,
                'impact_reduction': impact_reduction,
                'breakdown': breakdown,
                'has_controls': False
            }

        preventivo_controls = []
        detectivo_controls = []
        corretivo_controls = []

        for controle in controles:
            categorias = controle.categorias.all()
            for categoria in categorias:
                if 'preventivo' in categoria.tipo.lower():
                    preventivo_controls.append(controle)
                elif 'detectivo' in categoria.tipo.lower():
                    detectivo_controls.append(controle)
                elif 'corretivo' in categoria.tipo.lower():
                    corretivo_controls.append(controle)

        # Calculate reductions based on control types
        # Preventivo: 25% prob reduction per control, max 40%
        if preventivo_controls:
            prob_reduction += min(25 * len(preventivo_controls), 40)
            breakdown.append({
                'tipo': 'Preventivo',
                'quantidade': len(preventivo_controls),
                'reduz_probabilidade': True,
                'reduz_consequencia': False,
                'exemplo': 'Ex: firewall, controle de acesso'
            })

        # Detectivo: 15% prob + 20% impact per control, max 30% + 40%
        if detectivo_controls:
            prob_reduction += min(15 * len(detectivo_controls), 30)
            impact_reduction += min(20 * len(detectivo_controls), 40)
            breakdown.append({
                'tipo': 'Detectivo',
                'quantidade': len(detectivo_controls),
                'reduz_probabilidade': True,
                'reduz_consequencia': True,
                'exemplo': 'Ex: IDS, monitoramento, auditoria'
            })

        # Corretivo/Contingência: 30% impact reduction per control, max 40%
        if corretivo_controls:
            impact_reduction += min(30 * len(corretivo_controls), 40)
            breakdown.append({
                'tipo': 'Corretivo/Contingência',
                'quantidade': len(corretivo_controls),
                'reduz_probabilidade': False,
                'reduz_consequencia': True,
                'exemplo': 'Ex: backup, plano de recuperação, redundância'
            })

        # Ensure values don't exceed 100%
        prob_reduction = min(prob_reduction, 100)
        impact_reduction = min(impact_reduction, 100)

        return {
            'prob_reduction': prob_reduction,
            'impact_reduction': impact_reduction,
            'breakdown': breakdown,
            'has_controls': len(breakdown) > 0
        }

    @method_decorator(login_required(login_url="login"))
    def get(self, request, *args, **kwargs):
        """Display treatment form or list of risks requiring treatment."""

        if not self._check_permission(request.user):
            messages.error(request, "Você não tem permissão para acessar esta página.")
            return redirect('dashboard')

        from .models import Risco

        # Get risks that were evaluated and marked for treatment
        risco_id = request.GET.get('risco_id')

        risco_selecionado = None
        if risco_id:
            try:
                risco_selecionado = Risco.objects.get(id=risco_id)
            except Risco.DoesNotExist:
                messages.error(request, "Risco não encontrado.")
                risco_selecionado = None

        # Get all risks for treatment (excluding risks that have been accepted)
        # A risk is considered "accepted" if it has a tratamento with aceito=True
        from django.db.models import Q

        riscos_para_tratar = Risco.objects.exclude(
            tratamentos__aceito=True
        ).select_related(
            'ativo',
            'nivel_inerente',
            'consequencia_inerente',
            'probabilidade_inerente'
        ).distinct()

        # Get suggestions for selected risk
        sugestoes = None
        if risco_selecionado and risco_selecionado.nivel_inerente:
            sugestoes = self._get_suggestions_for_risk(risco_selecionado.nivel_inerente.categoria)

        # Initialize form with existing treatment data if available
        form_initial = {}
        control_reductions = None
        tratamento_existente = None

        if risco_selecionado:
            # Get existing treatments for this risk (most recent first)
            tratamentos = risco_selecionado.tratamentos.all().order_by('-id')

            if tratamentos.exists():
                # Use the most recent treatment
                tratamento_existente = tratamentos.first()

                # Pre-populate form with existing data
                form_initial = {
                    'nome': tratamento_existente.nome,
                    'tipo_tratamento': tratamento_existente.tipo_tratamento,
                    'descricao': tratamento_existente.descricao,
                    'reducao_probabilidade': tratamento_existente.reducao_probabilidade,
                    'reducao_impacto': tratamento_existente.reducao_impacto,
                    'controles': tratamento_existente.controles.all(),
                }

                # Calculate control reductions for display
                if tratamento_existente.controles.all().exists():
                    control_reductions = self._calculate_control_reductions(
                        tratamento_existente.controles.all()
                    )

        contexto = {
            'riscos_para_tratar': riscos_para_tratar,
            'risco_selecionado': risco_selecionado,
            'form': self.form_class(initial=form_initial),
            'sugestoes': sugestoes,
            'control_reductions': control_reductions,
            'tratamento_existente': tratamento_existente,
        }

        return render(request, self.template_name, contexto)

    @method_decorator(login_required(login_url="login"))
    def post(self, request, *args, **kwargs):
        """Process risk treatment plan creation or update."""

        if not self._check_permission(request.user):
            messages.error(request, "Você não tem permissão para acessar esta página.")
            return redirect('dashboard')

        from .models import Risco, Tratamento
        from django.utils import timezone

        form = self.form_class(request.POST)

        if form.is_valid():
            try:
                risco_id = request.POST.get('risco_id')
                risco = Risco.objects.get(id=risco_id)

                # Get form data
                nome = form.cleaned_data.get('nome')
                tipo_tratamento = form.cleaned_data.get('tipo_tratamento')
                descricao = form.cleaned_data.get('descricao')
                reducao_prob = form.cleaned_data.get('reducao_probabilidade', 0)
                reducao_impacto = form.cleaned_data.get('reducao_impacto', 0)
                controles = form.cleaned_data.get('controles', [])

                # Check if treatment already exists for this risk
                # If it does, update it instead of creating a new one
                tratamentos_existentes = risco.tratamentos.all()

                if tratamentos_existentes.exists():
                    # Update the most recent treatment
                    tratamento = tratamentos_existentes.order_by('-id').first()
                    tratamento.nome = nome
                    tratamento.tipo_tratamento = tipo_tratamento
                    tratamento.descricao = descricao
                    tratamento.reducao_probabilidade = reducao_prob
                    tratamento.reducao_impacto = reducao_impacto
                    tratamento.save()

                    # Update controls
                    if controles:
                        tratamento.controles.set(controles)
                    else:
                        tratamento.controles.clear()

                    action_message = "atualizado"
                else:
                    # Create new treatment plan
                    tratamento = Tratamento.objects.create(
                        nome=nome,
                        tipo_tratamento=tipo_tratamento,
                        descricao=descricao,
                        reducao_probabilidade=reducao_prob,
                        reducao_impacto=reducao_impacto,
                    )

                    # Link controls to treatment plan
                    if controles:
                        tratamento.controles.set(controles)

                    # Link treatment to risk
                    risco.tratamentos.add(tratamento)

                    action_message = "criado"

                # Calculate residual risk
                valor_residual, nivel_residual, calcs = self._calculate_residual_risk(
                    risco,
                    reducao_prob,
                    reducao_impacto
                )

                if valor_residual is not None:
                    risco.valor_risco_residual = valor_residual
                    risco.nivel_residual = nivel_residual

                # Update residual probability and consequence based on reductions
                if risco.probabilidade_inerente and risco.consequencia_inerente:
                    from .models import Probabilidade, Consequencia

                    # For now, keep the same probability/consequence objects
                    # but new risk value reflects the reduction
                    # In a more advanced implementation, we could create new P/C records
                    risco.probabilidade_residual = risco.probabilidade_inerente
                    risco.consequencia_residual = risco.consequencia_inerente

                risco.save()

                messages.success(request, f"Plano de tratamento {action_message} com sucesso!")
                return redirect('dashboard')

            except Risco.DoesNotExist:
                messages.error(request, "Risco não encontrado.")
                return redirect('tratamento_riscos')
            except Exception as e:
                messages.error(request, f"Erro ao processar plano de tratamento: {str(e)}")
                return redirect('tratamento_riscos')
        else:
            messages.error(request, "Formulário inválido. Verifique os dados inseridos.")
            contexto = {
                'form': form,
                'risco_selecionado': None,
                'riscos_para_tratar': Risco.objects.all(),
            }
            return render(request, self.template_name, contexto)


class GestaoIncidentesView(View):
    """View for managing security incidents (UC-10).

    Displays a list of all incidents with their current status and allows
    users to register new incidents or view existing ones.

    Authorized users:
    - Information Security Auditor (AUDITOR)
    - Security Analyst (ANALISTA)
    """
    template_name = "ismsapp/gestao_incidentes.html"

    def _check_permission(self, user):
        """Check if user has permission to manage incidents."""
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        allowed_actors = [
            UserProfile.Actor.AUDITOR,
            UserProfile.Actor.ANALISTA
        ]
        return user_profile.actor_type in allowed_actors

    @method_decorator(login_required(login_url="login"))
    def get(self, request, *args, **kwargs):
        """Display list of incidents and option to register new ones."""

        if not self._check_permission(request.user):
            messages.error(request, "Você não tem permissão para acessar esta página.")
            return redirect('dashboard')

        from .models import Incidente
        from django.db.models import Q

        search_query = request.GET.get('search', '').strip()
        selected_date = request.GET.get('data_incidente', '').strip()

        # Get all incidents ordered by date
        incidentes = Incidente.objects.all().select_related(
            'responsavel_tratamento',
            'registrado_por'
        ).prefetch_related('ativos_afetados')

        if search_query:
            incidentes = incidentes.filter(
                Q(numero_incidente__icontains=search_query) |
                Q(descricao__icontains=search_query) |
                Q(status__icontains=search_query)
            )

        if selected_date:
            incidentes = incidentes.filter(data_incidente=selected_date)

        # Get incident counts by status
        status_counts = {
            'registrado': Incidente.objects.filter(status=Incidente.StatusIncidente.REGISTRADO).count(),
            'em_investigacao': Incidente.objects.filter(status=Incidente.StatusIncidente.EM_INVESTIGACAO).count(),
            'resolvido': Incidente.objects.filter(status=Incidente.StatusIncidente.RESOLVIDO).count(),
            'fechado': Incidente.objects.filter(status=Incidente.StatusIncidente.FECHADO).count(),
            'total': incidentes.count(),
        }

        # Get reports generated
        relatorios_gerados = incidentes.filter(relatorio_gerado=True).count()

        contexto = {
            'incidentes': incidentes,
            'status_counts': status_counts,
            'relatorios_gerados': relatorios_gerados,
            'search_query': search_query,
            'selected_date': selected_date,
        }

        return render(request, self.template_name, contexto)

class CadastroIncidenteView(View):
    """View for registering new security incidents (UC-10, Step 1-4).

    Allows authorized users to register new incidents with:
    - Description of the incident
    - Date and time of occurrence
    - Affected assets

    The system automatically generates an incident number and records
    who registered the incident and when.

    Authorized users:
    - Information Security Auditor (AUDITOR)
    - Security Analyst (ANALISTA)
    """
    form_class = CadastroIncidenteForm
    template_name = "ismsapp/cadastro_incidente.html"

    def _check_permission(self, user):
        """Check if user has permission to register incidents."""
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        allowed_actors = [
            UserProfile.Actor.AUDITOR,
            UserProfile.Actor.ANALISTA
        ]
        return user_profile.actor_type in allowed_actors

    def _generate_incident_number(self):
        """Generate a unique incident number (INC-YYYY-NNNN format)."""
        from .models import Incidente
        from datetime import datetime

        year = datetime.now().year
        # Count incidents for this year
        count = Incidente.objects.filter(
            numero_incidente__startswith=f"INC-{year}-"
        ).count() + 1

        return f"INC-{year}-{count:04d}"

    @method_decorator(login_required(login_url="login"))
    def get(self, request, *args, **kwargs):
        """Display incident registration form."""

        if not self._check_permission(request.user):
            messages.error(request, "Você não tem permissão para acessar esta página.")
            return redirect('dashboard')

        form = self.form_class()
        contexto = {'form': form}
        return render(request, self.template_name, contexto)

    @method_decorator(login_required(login_url="login"))
    def post(self, request, *args, **kwargs):
        """Process incident registration form."""

        if not self._check_permission(request.user):
            messages.error(request, "Você não tem permissão para acessar esta página.")
            return redirect('dashboard')

        form = self.form_class(request.POST)

        if form.is_valid():
            try:
                from .models import Incidente

                # Create incident with auto-generated number
                incidente = form.save(commit=False)
                incidente.numero_incidente = self._generate_incident_number()
                incidente.registrado_por = request.user
                incidente.status = Incidente.StatusIncidente.REGISTRADO
                incidente.save()

                # Save many-to-many relationships
                form.save_m2m()

                messages.success(
                    request,
                    f"Incidente {incidente.numero_incidente} registrado com sucesso!"
                )
                return redirect('gestao_incidentes')

            except Exception as e:
                messages.error(
                    request,
                    f"Erro ao registrar incidente: {str(e)}"
                )
                contexto = {'form': form}
                return render(request, self.template_name, contexto)
        else:
            contexto = {'form': form}
            return render(request, self.template_name, contexto)


class VisualizarIncidenteView(View):
    """View for viewing incident details and managing status (UC-10, Steps 5-6).

    Allows authorized users to:
    - View incident details
    - Assign responsible person for treatment
    - Update incident status
    - Generate final report

    Authorized users:
    - Information Security Auditor (AUDITOR)
    - Security Analyst (ANALISTA)
    """
    template_name = "ismsapp/visualizar_incidente.html"

    def _check_permission(self, user):
        """Check if user has permission to view/edit incidents."""
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        allowed_actors = [
            UserProfile.Actor.AUDITOR,
            UserProfile.Actor.ANALISTA
        ]
        return user_profile.actor_type in allowed_actors

    @method_decorator(login_required(login_url="login"))
    def get(self, request, incidente_id, *args, **kwargs):
        """Display incident details and status update form."""

        if not self._check_permission(request.user):
            messages.error(request, "Você não tem permissão para acessar esta página.")
            return redirect('dashboard')

        try:
            from .models import Incidente
            incidente = Incidente.objects.prefetch_related('ativos_afetados').get(id=incidente_id)
        except:
            messages.error(request, "Incidente não encontrado.")
            return redirect('gestao_incidentes')

        form = AtribuirResponsavelIncidenteForm(instance=incidente)

        # Check if report has been generated
        has_relatorio = hasattr(incidente, 'relatorio')

        contexto = {
            'incidente': incidente,
            'form': form,
            'has_relatorio': has_relatorio,
        }
        return render(request, self.template_name, contexto)

    @method_decorator(login_required(login_url="login"))
    def post(self, request, incidente_id, *args, **kwargs):
        """Process incident status update."""

        if not self._check_permission(request.user):
            messages.error(request, "Você não tem permissão para acessar esta página.")
            return redirect('dashboard')

        try:
            from .models import Incidente
            incidente = Incidente.objects.get(id=incidente_id)
        except:
            messages.error(request, "Incidente não encontrado.")
            return redirect('gestao_incidentes')

        form = AtribuirResponsavelIncidenteForm(request.POST, instance=incidente)

        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Incidente atualizado com sucesso!")
                return redirect('visualizar_incidente', incidente_id=incidente_id)
            except Exception as e:
                messages.error(request, f"Erro ao atualizar incidente: {str(e)}")

        contexto = {
            'incidente': incidente,
            'form': form,
            'has_relatorio': hasattr(incidente, 'relatorio'),
        }
        return render(request, self.template_name, contexto)


class GerarRelatórioIncidenteView(View):
    """View for generating the final incident report (UC-10, Steps 7-8).

    Allows authorized users to create the comprehensive final report with:
    - Event description
    - Affected assets details
    - Remediation actions taken
    - Root cause analysis
    - Impact analysis (financial, operational, image)
    - Lessons learned

    The system stores the report and marks the incident as having a report.

    Authorized users:
    - Information Security Auditor (AUDITOR)
    - Security Analyst (ANALISTA)
    """
    form_class = GerarRelatórioIncidenteForm
    template_name = "ismsapp/gerar_relatorio_incidente.html"

    def _check_permission(self, user):
        """Check if user has permission to generate reports."""
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        allowed_actors = [
            UserProfile.Actor.AUDITOR,
            UserProfile.Actor.ANALISTA
        ]
        return user_profile.actor_type in allowed_actors

    def _generate_protocolo(self):
        """Generate a unique protocol number for the report."""
        from .models import RelatórioIncidente
        from datetime import datetime

        year = datetime.now().year
        count = RelatórioIncidente.objects.filter(
            protocolo__startswith=f"INC-{year}-"
        ).count() + 1

        return f"INC-{year}-{count:04d}"

    @method_decorator(login_required(login_url="login"))
    def get(self, request, incidente_id, *args, **kwargs):
        """Display report generation form."""

        if not self._check_permission(request.user):
            messages.error(request, "Você não tem permissão para acessar esta página.")
            return redirect('dashboard')

        try:
            from .models import Incidente, RelatórioIncidente
            incidente = Incidente.objects.get(id=incidente_id)

            # Check if report already exists
            if hasattr(incidente, 'relatorio'):
                return redirect('relatorio_incidente', relatorio_id=incidente.relatorio.id)

        except:
            messages.error(request, "Incidente não encontrado.")
            return redirect('gestao_incidentes')

        form = self.form_class()

        contexto = {
            'incidente': incidente,
            'form': form,
        }
        return render(request, self.template_name, contexto)

    @method_decorator(login_required(login_url="login"))
    def post(self, request, incidente_id, *args, **kwargs):
        """Process report generation."""

        if not self._check_permission(request.user):
            messages.error(request, "Você não tem permissão para acessar esta página.")
            return redirect('dashboard')

        try:
            from .models import Incidente, RelatórioIncidente
            incidente = Incidente.objects.get(id=incidente_id)
        except:
            messages.error(request, "Incidente não encontrado.")
            return redirect('gestao_incidentes')

        form = self.form_class(request.POST)

        if form.is_valid():
            try:
                # Create report
                relatorio = form.save(commit=False)
                relatorio.incidente = incidente
                relatorio.protocolo = self._generate_protocolo()
                relatorio.responsavel_tratamento = incidente.responsavel_tratamento
                relatorio.status_relatorio = RelatórioIncidente.StatusRelatorio.FINAL
                relatorio.save()

                # Mark incident as having a report
                incidente.relatorio_gerado = True
                incidente.status = Incidente.StatusIncidente.FECHADO
                incidente.save()

                messages.success(
                    request,
                    f"Relatório {relatorio.protocolo} gerado com sucesso!"
                )
                return redirect('relatorio_incidente', relatorio_id=relatorio.id)

            except Exception as e:
                messages.error(request, f"Erro ao gerar relatório: {str(e)}")
                contexto = {
                    'incidente': incidente,
                    'form': form,
                }
                return render(request, self.template_name, contexto)
        else:
            contexto = {
                'incidente': incidente,
                'form': form,
            }
            return render(request, self.template_name, contexto)


class RelatórioIncidenteView(View):
    """View for displaying the final incident report.

    Shows all sections of the report:
    - Incident identification
    - Event description
    - Affected assets
    - Actions taken
    - Responsible person
    - Root cause analysis
    - Impact analysis
    - Lessons learned

    Also provides option to download the report.
    """
    template_name = "ismsapp/relatorio_incidente.html"

    def _check_permission(self, user):
        """Check if user has permission to view reports."""
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        allowed_actors = [
            UserProfile.Actor.AUDITOR,
            UserProfile.Actor.ANALISTA
        ]
        return user_profile.actor_type in allowed_actors

    @method_decorator(login_required(login_url="login"))
    def get(self, request, relatorio_id, *args, **kwargs):
        """Display incident report."""

        if not self._check_permission(request.user):
            messages.error(request, "Você não tem permissão para acessar esta página.")
            return redirect('dashboard')

        try:
            from .models import RelatórioIncidente
            relatorio = RelatórioIncidente.objects.select_related(
                'incidente',
                'responsavel_tratamento'
            ).get(id=relatorio_id)
        except:
            messages.error(request, "Relatório não encontrado.")
            return redirect('gestao_incidentes')

        contexto = {
            'relatorio': relatorio,
            'incidente': relatorio.incidente,
        }
        return render(request, self.template_name, contexto)

class DeleteIncidenteView(View):
    """View for deleting incidents with confirmation.

    Allows authorized users to:
    - View incident details
    - Confirm deletion
    - Delete the incident permanently

    Authorized users:
    - Information Security Auditor (AUDITOR)
    - Security Analyst (ANALISTA)
    """
    template_name = "ismsapp/deletar_incidente.html"

    def _check_permission(self, user):
        """Check if user has permission to delete incidents."""
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        allowed_actors = [
            UserProfile.Actor.AUDITOR,
            UserProfile.Actor.ANALISTA
        ]
        return user_profile.actor_type in allowed_actors

    @method_decorator(login_required(login_url="login"))
    def get(self, request, incidente_id, *args, **kwargs):
        """Display incident deletion confirmation page."""

        if not self._check_permission(request.user):
            messages.error(request, "Você não tem permissão para acessar esta página.")
            return redirect('dashboard')

        try:
            from .models import Incidente
            incidente = Incidente.objects.prefetch_related('ativos_afetados').get(id=incidente_id)
        except:
            messages.error(request, "Incidente não encontrado.")
            return redirect('gestao_incidentes')

        contexto = {
            'incidente': incidente,
        }
        return render(request, self.template_name, contexto)

    @method_decorator(login_required(login_url="login"))
    def post(self, request, incidente_id, *args, **kwargs):
        """Process incident deletion."""

        if not self._check_permission(request.user):
            messages.error(request, "Você não tem permissão para acessar esta página.")
            return redirect('dashboard')

        try:
            from .models import Incidente
            incidente = Incidente.objects.get(id=incidente_id)
            numero_incidente = incidente.numero_incidente
            incidente.delete()
            messages.success(request, f"Incidente {numero_incidente} deletado com sucesso!")
            return redirect('gestao_incidentes')
        except Exception as e:
            messages.error(request, f"Erro ao deletar incidente: {str(e)}")
            return redirect('gestao_incidentes')


#Threats CRUD
class DeteccaoAmeacaView(View):
    """View for threat detection (Detecção de Ameaças).

    This view allows authorized users (Security Analysts and Auditors) to:
    1. View the list of monitored assets
    2. Register new threats
    3. Associate threats to potentially affected assets
    4. Record description, origin, and possible impacts

    Requires:
    - User must be authenticated
    - User must be either an Auditor or Analyst

    UC-11 - Detecção de Ameaças
    """
    form_class = AmeacaForm
    template_name = "ismsapp/deteccao_ameaca.html"

    def _check_permission(self, user):
        """Check if user has permission to detect threats."""
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        # Only Security Auditor and Analyst can detect threats
        allowed_actors = [
            UserProfile.Actor.AUDITOR,
            UserProfile.Actor.ANALISTA
        ]
        return user_profile.actor_type in allowed_actors

    @method_decorator(login_required(login_url="login"))
    def get(self, request, *args, **kwargs):
        """Display threat detection page with list of monitored assets and form."""
        if not self._check_permission(request.user):
            messages.error(request, "Você não tem permissão para acessar esta página.")
            return redirect('dashboard')

        from .models import Ativo, Ameaca

        # Get all assets
        ativos = Ativo.objects.all()

        # Get all threats with their associated assets
        ameacas = Ameaca.objects.prefetch_related('ativos').all()

        contexto = {
            'form': self.form_class(),
            'ativos': ativos,
            'ameacas': ameacas,
        }
        return render(request, self.template_name, contexto)

    @method_decorator(login_required(login_url="login"))
    def post(self, request, *args, **kwargs):
        """Handle threat registration."""
        if not self._check_permission(request.user):
            messages.error(request, "Você não tem permissão para acessar esta página.")
            return redirect('dashboard')

        from .models import Ativo, Ameaca

        form = self.form_class(request.POST)

        if form.is_valid():
            try:
                # Extract the data
                ativos_selecionados = form.cleaned_data.get('ativos')
                nome = form.cleaned_data.get('nome')

                # Create the threat
                ameaca = Ameaca.objects.create(
                    nome=nome
                )

                # Add the selected assets to the threat
                ameaca.ativos.set(ativos_selecionados)

                # Get names of affected assets
                ativos_nomes = ", ".join([a.nome for a in ativos_selecionados])

                messages.success(
                    request,
                    f"Ameaça '{nome}' registrada com sucesso para os ativos: {ativos_nomes}."
                )

                # Reload the page with updated data
                ativos = Ativo.objects.all()
                ameacas = Ameaca.objects.prefetch_related('ativos').all()

                contexto = {
                    'form': self.form_class(),
                    'ativos': ativos,
                    'ameacas': ameacas,
                }
                return render(request, self.template_name, contexto)

            except Exception as e:
                messages.error(request, f"Erro ao registrar ameaça: {str(e)}")
                ativos = Ativo.objects.all()
                ameacas = Ameaca.objects.prefetch_related('ativos').all()

                contexto = {
                    'form': form,
                    'ativos': ativos,
                    'ameacas': ameacas,
                }
                return render(request, self.template_name, contexto)

        else:
            # Form has errors
            ativos = Ativo.objects.all()
            ameacas = Ameaca.objects.prefetch_related('ativos').all()

            contexto = {
                'form': form,
                'ativos': ativos,
                'ameacas': ameacas,
            }
            return render(request, self.template_name, contexto)

class ReadAmeacaView(View):
    """View para listar ameaças.

    Esta view permite que os usuários visualizem todas as ameaças identificadas
    no sistema.
    """
    template_name = "ismsapp/lista_ameacas.html"

    def _check_permission(self, user):
        """Check if user has permission to view threats."""
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        # All authenticated users can view threats
        return True

    def _check_edit_permission(self, user):
        """Check if user has permission to edit/delete threats."""
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        allowed_actors = [
            UserProfile.Actor.AUDITOR,
            UserProfile.Actor.ANALISTA
        ]
        return user_profile.actor_type in allowed_actors

    @method_decorator(login_required(login_url="login"))
    def get(self, request, *args, **kwargs):
        if not self._check_permission(request.user):
            return redirect('dashboard')

        from .models import Ameaca
        from django.db.models import Q

        search_query = request.GET.get('search', '').strip()

        ameacas = Ameaca.objects.all()
        if search_query:
            ameacas = ameacas.filter(
                Q(nome__icontains=search_query) |
                Q(ativos__nome__icontains=search_query)
            ).distinct()

        pode_editar_deletar = self._check_edit_permission(request.user)

        contexto = {
            'ameacas': ameacas,
            'pode_editar_deletar': pode_editar_deletar,
            'search_query': search_query,
        }
        return render(request, self.template_name, contexto)


class UpdateAmeacaView(View):
    """View para edição/atualização de ameaça.

    Esta view permite que os usuários cadastrados como Auditor ou Analista de Segurança
    editem ameaças existentes.
    Requer que o usuário esteja autenticado e tenha permissão apropriada.

    Usuarios autorizados:
    - Auditor de Segurança (AUDITOR)
    - Analista de Segurança (ANALISTA)
    """
    form_class = AmeacaForm
    template_name = "ismsapp/editar_ameaca.html"

    def _check_permission(self, user):
        """Check if user has permission to update threats."""
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        allowed_actors = [
            UserProfile.Actor.AUDITOR,
            UserProfile.Actor.ANALISTA
        ]
        return user_profile.actor_type in allowed_actors

    @method_decorator(login_required(login_url="login"))
    def get(self, request, ameaca_id=None, *args, **kwargs):
        if not self._check_permission(request.user):
            return redirect('dashboard')

        from .models import Ameaca

        if not ameaca_id:
            return redirect('lista_ameacas')

        try:
            ameaca = Ameaca.objects.get(id=ameaca_id)
        except Ameaca.DoesNotExist:
            return redirect('lista_ameacas')

        form = self.form_class(instance=ameaca)
        contexto = {
            'form': form,
            'ameaca': ameaca,
            'ameaca_id': ameaca_id,
        }
        return render(request, self.template_name, contexto)

    @method_decorator(login_required(login_url="login"))
    def post(self, request, ameaca_id=None, *args, **kwargs):
        if not self._check_permission(request.user):
            return redirect('dashboard')

        from .models import Ameaca

        if not ameaca_id:
            return redirect('lista_ameacas')

        try:
            ameaca = Ameaca.objects.get(id=ameaca_id)
        except Ameaca.DoesNotExist:
            return redirect('lista_ameacas')

        form = self.form_class(request.POST, instance=ameaca)
        if form.is_valid():
            form.save()
            return redirect('lista_ameacas')

        contexto = {
            'form': form,
            'ameaca': ameaca,
            'ameaca_id': ameaca_id,
        }
        return render(request, self.template_name, contexto)


class DeleteAmeacaView(View):
    """View para deletar ameaça.

    Esta view permite que os usuários cadastrados como Auditor ou Analista de Segurança
    deletem ameaças existentes.
    Requer que o usuário esteja autenticado e tenha permissão apropriada.

    Usuarios autorizados:
    - Auditor de Segurança (AUDITOR)
    - Analista de Segurança (ANALISTA)
    """
    template_name = "ismsapp/deletar_ameaca.html"

    def _check_permission(self, user):
        """Check if user has permission to delete threats."""
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        allowed_actors = [
            UserProfile.Actor.AUDITOR,
            UserProfile.Actor.ANALISTA
        ]
        return user_profile.actor_type in allowed_actors

    @method_decorator(login_required(login_url="login"))
    def get(self, request, ameaca_id=None, *args, **kwargs):
        if not self._check_permission(request.user):
            return redirect('dashboard')

        from .models import Ameaca

        if not ameaca_id:
            return redirect('lista_ameacas')

        try:
            ameaca = Ameaca.objects.get(id=ameaca_id)
        except Ameaca.DoesNotExist:
            return redirect('lista_ameacas')

        contexto = {
            'ameaca': ameaca,
            'ameaca_id': ameaca_id,
        }
        return render(request, self.template_name, contexto)

    @method_decorator(login_required(login_url="login"))
    def post(self, request, ameaca_id=None, *args, **kwargs):
        if not self._check_permission(request.user):
            return redirect('dashboard')

        from .models import Ameaca

        if not ameaca_id:
            return redirect('lista_ameacas')

        try:
            ameaca = Ameaca.objects.get(id=ameaca_id)
            ameaca.delete()
            return redirect('lista_ameacas')
        except Ameaca.DoesNotExist:
            return redirect('lista_ameacas')

#vulnerabilidades CRUD
class VulnerabilidadeView(View):
    """View for vulnerability management (Gestão de Vulnerabilidades).

    This view allows authorized users (Security Analysts and Auditors) to:
    1. Register new vulnerabilities in assets
    2. Specify severity level and correction priority
    3. Track vulnerability status
    4. View historical resolution records

    Requires:
    - User must be authenticated
    - User must be either an Auditor or Analyst

    UC-13 - Gestão de Vulnerabilidades
    """
    form_class = VulnerabilidadeForm
    template_name = "ismsapp/gestao_vulnerabilidades.html"

    def _check_permission(self, user):
        """Check if user has permission to manage vulnerabilities."""
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        # Only Security Auditor and Analyst can manage vulnerabilities
        allowed_actors = [
            UserProfile.Actor.AUDITOR,
            UserProfile.Actor.ANALISTA
        ]
        return user_profile.actor_type in allowed_actors

    @method_decorator(login_required(login_url="login"))
    def get(self, request, *args, **kwargs):
        """Display vulnerability management page with form and vulnerability list."""
        if not self._check_permission(request.user):
            messages.error(request, "Você não tem permissão para acessar esta página.")
            return redirect('dashboard')

        from .models import Vulnerabilidade

        # Get all vulnerabilities ordered by name
        vulnerabilidades = Vulnerabilidade.objects.select_related('ativo').order_by('nome')

        # Calculate total vulnerabilities
        total = vulnerabilidades.count()

        contexto = {
            'form': self.form_class(),
            'vulnerabilidades': vulnerabilidades,
            'total_vulnerabilidades': total,
        }
        return render(request, self.template_name, contexto)

    @method_decorator(login_required(login_url="login"))
    def post(self, request, *args, **kwargs):
        """Handle vulnerability registration."""
        if not self._check_permission(request.user):
            messages.error(request, "Você não tem permissão para acessar esta página.")
            return redirect('dashboard')

        from .models import Vulnerabilidade

        form = self.form_class(request.POST)

        if form.is_valid():
            try:
                # Extract the data
                ameacas = form.cleaned_data.get('ameacas')
                ativo = form.cleaned_data.get('ativo')
                nome = form.cleaned_data.get('nome')

                # Check if vulnerability with same ativo and nome already exists
                existing = Vulnerabilidade.objects.filter(
                    ativo=ativo,
                    nome=nome
                ).first()

                if existing:
                    messages.warning(
                        request,
                        f"Vulnerabilidade '{nome}' já registrada para este ativo. "
                        f"ID: VUL-{existing.pk:04d}"
                    )
                else:
                    # Create the vulnerability
                    vulnerabilidade = Vulnerabilidade.objects.create(
                        ativo=ativo,
                        nome=nome
                    )

                    # Set the multiple threats
                    if ameacas:
                        vulnerabilidade.ameacas.set(ameacas)

                    messages.success(
                        request,
                        f"Vulnerabilidade registrada com sucesso! "
                        f"ID: VUL-{vulnerabilidade.pk:04d} | {ativo.nome}"
                    )

            except Exception as e:
                messages.error(request, f"Erro ao registrar vulnerabilidade: {str(e)}")

        else:
            # Form has errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

        # Redirect to the same page
        return redirect('gestao_vulnerabilidades')

class ReadVulnerabilidadeView(View):
    """View for reading/listing vulnerabilities.

    This view displays all registered vulnerabilities with filtering options.
    Requires user authentication and appropriate permissions.
    """
    template_name = "ismsapp/lista_vulnerabilidades.html"

    def _check_permission(self, user):
        """Check if user has permission to view vulnerabilities."""
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        allowed_actors = [
            UserProfile.Actor.AUDITOR,
            UserProfile.Actor.ANALISTA
        ]
        return user_profile.actor_type in allowed_actors

    @method_decorator(login_required(login_url="login"))
    def get(self, request, *args, **kwargs):
        """Display all vulnerabilities."""
        if not self._check_permission(request.user):
            messages.error(request, "Você não tem permissão para acessar esta página.")
            return redirect('dashboard')

        from .models import Vulnerabilidade
        from django.db.models import Q

        search_query = request.GET.get('search', '').strip()

        vulnerabilidades = Vulnerabilidade.objects.select_related('ativo').prefetch_related('ameacas').order_by('nome')

        if search_query:
            vulnerabilidades = vulnerabilidades.filter(
                Q(nome__icontains=search_query) |
                Q(ativo__nome__icontains=search_query) |
                Q(ameacas__nome__icontains=search_query)
            ).distinct()

        total = vulnerabilidades.count()

        contexto = {
            'vulnerabilidades': vulnerabilidades,
            'total_vulnerabilidades': total,
            'search_query': search_query,
        }
        return render(request, self.template_name, contexto)


class UpdateVulnerabilidadeView(View):
    """View for updating/editing vulnerabilities.

    This view allows authorized users (Security Analysts and Auditors) to edit
    existing vulnerabilities including severity, priority, status, and description.

    Requires user authentication and appropriate permissions.
    """
    form_class = VulnerabilidadeUpdateForm
    template_name = "ismsapp/editar_vulnerabilidade.html"

    def _check_permission(self, user):
        """Check if user has permission to update vulnerabilities."""
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        allowed_actors = [
            UserProfile.Actor.AUDITOR,
            UserProfile.Actor.ANALISTA
        ]
        return user_profile.actor_type in allowed_actors

    @method_decorator(login_required(login_url="login"))
    def get(self, request, vulnerabilidade_id=None, *args, **kwargs):
        """Display vulnerability edit form."""
        if not self._check_permission(request.user):
            return redirect('dashboard')

        from .models import Vulnerabilidade

        if not vulnerabilidade_id:
            return redirect('lista_vulnerabilidades')

        try:
            vulnerabilidade = Vulnerabilidade.objects.select_related('ativo').prefetch_related('ameacas').get(id=vulnerabilidade_id)
        except Vulnerabilidade.DoesNotExist:
            messages.error(request, "Vulnerabilidade não encontrada.")
            return redirect('lista_vulnerabilidades')

        form = self.form_class(instance=vulnerabilidade)
        contexto = {
            'form': form,
            'vulnerabilidade': vulnerabilidade,
            'vulnerabilidade_id': vulnerabilidade_id,
        }
        return render(request, self.template_name, contexto)

    @method_decorator(login_required(login_url="login"))
    def post(self, request, vulnerabilidade_id=None, *args, **kwargs):
        """Handle vulnerability update."""
        if not self._check_permission(request.user):
            return redirect('dashboard')

        from .models import Vulnerabilidade

        if not vulnerabilidade_id:
            return redirect('lista_vulnerabilidades')

        try:
            vulnerabilidade = Vulnerabilidade.objects.get(id=vulnerabilidade_id)
        except Vulnerabilidade.DoesNotExist:
            messages.error(request, "Vulnerabilidade não encontrada.")
            return redirect('lista_vulnerabilidades')

        form = self.form_class(request.POST, instance=vulnerabilidade)
        if form.is_valid():
            form.save()
            messages.success(request, f"Vulnerabilidade VUL-{vulnerabilidade.id:04d} atualizada com sucesso!")
            return redirect('lista_vulnerabilidades')

        contexto = {
            'form': form,
            'vulnerabilidade': vulnerabilidade,
            'vulnerabilidade_id': vulnerabilidade_id,
        }
        return render(request, self.template_name, contexto)


class DeleteVulnerabilidadeView(View):
    """View for deleting vulnerabilities.

    This view allows authorized users (Security Analysts and Auditors) to delete
    existing vulnerabilities. Displays confirmation page before deletion.

    Requires user authentication and appropriate permissions.
    """
    template_name = "ismsapp/deletar_vulnerabilidade.html"

    def _check_permission(self, user):
        """Check if user has permission to delete vulnerabilities."""
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        allowed_actors = [
            UserProfile.Actor.AUDITOR,
            UserProfile.Actor.ANALISTA
        ]
        return user_profile.actor_type in allowed_actors

    @method_decorator(login_required(login_url="login"))
    def get(self, request, vulnerabilidade_id=None, *args, **kwargs):
        """Display vulnerability deletion confirmation page."""
        if not self._check_permission(request.user):
            return redirect('dashboard')

        from .models import Vulnerabilidade

        if not vulnerabilidade_id:
            return redirect('lista_vulnerabilidades')

        try:
            vulnerabilidade = Vulnerabilidade.objects.select_related('ativo').prefetch_related('ameacas').get(id=vulnerabilidade_id)
        except Vulnerabilidade.DoesNotExist:
            messages.error(request, "Vulnerabilidade não encontrada.")
            return redirect('lista_vulnerabilidades')

        contexto = {
            'vulnerabilidade': vulnerabilidade,
            'vulnerabilidade_id': vulnerabilidade_id,
        }
        return render(request, self.template_name, contexto)

    @method_decorator(login_required(login_url="login"))
    def post(self, request, vulnerabilidade_id=None, *args, **kwargs):
        """Handle vulnerability deletion."""
        if not self._check_permission(request.user):
            return redirect('dashboard')

        from .models import Vulnerabilidade

        if not vulnerabilidade_id:
            return redirect('lista_vulnerabilidades')

        try:
            vulnerabilidade = Vulnerabilidade.objects.get(id=vulnerabilidade_id)
            vuln_id = vulnerabilidade.id
            vulnerabilidade.delete()
            messages.success(request, f"Vulnerabilidade VUL-{vuln_id:04d} deletada com sucesso!")
            return redirect('lista_vulnerabilidades')
        except Vulnerabilidade.DoesNotExist:
            messages.error(request, "Vulnerabilidade não encontrada.")
            return redirect('lista_vulnerabilidades')

#auditorias CRUD
class RegistroAuditoriaView(View):
    """View for audit registration and tracking (Registro de Auditorias).

    This view allows authorized users (Security Auditors) to:
    1. Register new internal and external audits
    2. Record identified non-conformities
    3. Define remediation action plans
    4. Track audit status and non-conformity resolution

    Requires:
    - User must be authenticated
    - User must be a Security Auditor

    UC-15 - Gestão de Auditorias Internas e Externas
    """
    form_class = AuditoriaForm
    template_name = "ismsapp/registro_auditoria.html"

    def _check_permission(self, user):
        """Check if user has permission to manage audits."""
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        # Only Security Auditor can register audits
        return user_profile.actor_type == UserProfile.Actor.AUDITOR

    @method_decorator(login_required(login_url="login"))
    def get(self, request, *args, **kwargs):
        """Display audit registration page with form."""
        if not self._check_permission(request.user):
            messages.error(request, "Você não tem permissão para acessar esta página.")
            return redirect('dashboard')

        contexto = {
            'form': self.form_class(),
        }
        return render(request, self.template_name, contexto)

    @method_decorator(login_required(login_url="login"))
    def post(self, request, *args, **kwargs):
        """Handle audit registration."""
        if not self._check_permission(request.user):
            messages.error(request, "Você não tem permissão para acessar esta página.")
            return redirect('dashboard')

        from .models import Auditoria

        form = self.form_class(request.POST)

        if form.is_valid():
            try:
                # Extract the data
                tipo_auditoria = form.cleaned_data.get('tipo_auditoria')
                nome = form.cleaned_data.get('nome')
                data_auditoria = form.cleaned_data.get('data_auditoria')
                nao_conformidades_identificadas = form.cleaned_data.get('nao_conformidades_identificadas')
                nao_conformidades = form.cleaned_data.get('nao_conformidades')
                plano_acao = form.cleaned_data.get('plano_acao')

                # Check if audit already exists with same name and date
                existentes = Auditoria.objects.filter(
                    nome=nome,
                    data_auditoria=data_auditoria
                ).first()

                if existentes:
                    messages.warning(
                        request,
                        f"Auditoria já registrada: {nome} em {data_auditoria}. "
                        f"Status: {existentes.get_status_display()}"
                    )
                else:
                    # Determine status based on whether non-conformities were identified
                    status = Auditoria.StatusAuditoria.CONCLUIDA if not nao_conformidades_identificadas else Auditoria.StatusAuditoria.PENDENTE

                    # Create the audit
                    auditoria = Auditoria.objects.create(
                        tipo_auditoria=tipo_auditoria,
                        nome=nome,
                        data_auditoria=data_auditoria,
                        nao_conformidades_identificadas=nao_conformidades_identificadas,
                        nao_conformidades=nao_conformidades,
                        plano_acao=plano_acao,
                        status=status,
                        registrado_por=request.user
                    )

                    messages.success(
                        request,
                        f"Auditoria '{nome}' registrada com sucesso! "
                        f"Tipo: {auditoria.get_tipo_auditoria_display()} | "
                        f"Status: {auditoria.get_status_display()}"
                    )

            except Exception as e:
                messages.error(request, f"Erro ao registrar auditoria: {str(e)}")

        else:
            # Form has errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

        # Redirect to the list page after registration
        return redirect('lista_auditorias')


class ReadAuditoriaView(View):
    """View for reading/listing auditorias.

    This view displays all registered audits with filtering options.
    Requires user authentication and appropriate permissions (Auditor only).
    """
    template_name = "ismsapp/lista_auditorias.html"

    def _check_permission(self, user):
        """Check if user has permission to view audits."""
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        return user_profile.actor_type == UserProfile.Actor.AUDITOR

    @method_decorator(login_required(login_url="login"))
    def get(self, request, *args, **kwargs):
        """Display all audits."""
        if not self._check_permission(request.user):
            messages.error(request, "Você não tem permissão para acessar esta página.")
            return redirect('dashboard')

        from .models import Auditoria, Incidente, Risco, Controle
        from datetime import timedelta
        from django.utils import timezone
        from django.db.models import Q

        search_query = request.GET.get('search', '').strip()

        # Risks
        riscos = Risco.objects.filter(nivel_inerente__isnull=False).order_by('-id')

        # Audits
        auditorias = Auditoria.objects.all().order_by('-data_auditoria')

        # Controls
        controles = Controle.objects.prefetch_related('categorias').all().order_by('nome')

        # Incidents - get recent incidents (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        incidentes = Incidente.objects.filter(
            data_registro__gte=thirty_days_ago
        ).order_by('-data_incidente')

        if search_query:
            riscos = riscos.filter(
                Q(nome__icontains=search_query) |
                Q(ativo__nome__icontains=search_query)
            )

            auditorias = auditorias.filter(
                Q(nome__icontains=search_query) |
                Q(tipo_auditoria__icontains=search_query) |
                Q(status__icontains=search_query)
            )

            incidentes = incidentes.filter(
                Q(numero_incidente__icontains=search_query) |
                Q(descricao__icontains=search_query) |
                Q(status__icontains=search_query)
            )

            controles = controles.filter(
                Q(nome__icontains=search_query) |
                Q(descricao__icontains=search_query) |
                Q(categorias__tipo__icontains=search_query)
            ).distinct()

        # Metrics
        # Active risks (all risks with inerente level assigned)
        try:
            count_active_risks = Risco.objects.filter(nivel_inerente__isnull=False).count()
        except:
            count_active_risks = 0

        # Implemented controls (all controls)
        try:
            count_controls = Controle.objects.count()
        except:
            count_controls = 0

        # Recent incidents
        count_recent_incidents = incidentes.count()

        # Status counts
        pendentes = auditorias.filter(status='pendente').count()
        concluidas = auditorias.filter(status='concluida').count()

        contexto = {
            'riscos': riscos,
            'auditorias': auditorias,
            'controles': controles,
            'incidentes': incidentes,
            'count_pendentes': pendentes,
            'count_concluidas': concluidas,
            'count_active_risks': count_active_risks,
            'count_controls': count_controls,
            'count_recent_incidents': count_recent_incidents,
            'search_query': search_query,
        }
        return render(request, self.template_name, contexto)


class UpdateAuditoriaView(View):
    """View for updating/editing audits.

    This view allows authorized users (Auditors) to edit
    existing audits including type, name, date, findings, and action plans.

    Requires user authentication and appropriate permissions.
    """
    form_class = AuditoriaForm
    template_name = "ismsapp/editar_auditoria.html"

    def _check_permission(self, user):
        """Check if user has permission to update audits."""
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        return user_profile.actor_type == UserProfile.Actor.AUDITOR

    @method_decorator(login_required(login_url="login"))
    def get(self, request, auditoria_id=None, *args, **kwargs):
        """Display audit edit form."""
        if not self._check_permission(request.user):
            return redirect('dashboard')

        from .models import Auditoria

        if not auditoria_id:
            return redirect('lista_auditorias')

        try:
            auditoria = Auditoria.objects.get(id=auditoria_id)
        except Auditoria.DoesNotExist:
            messages.error(request, "Auditoria não encontrada.")
            return redirect('lista_auditorias')

        form = self.form_class(instance=auditoria)
        contexto = {
            'form': form,
            'auditoria': auditoria,
            'auditoria_id': auditoria_id,
        }
        return render(request, self.template_name, contexto)

    @method_decorator(login_required(login_url="login"))
    def post(self, request, auditoria_id=None, *args, **kwargs):
        """Handle audit update."""
        if not self._check_permission(request.user):
            return redirect('dashboard')

        from .models import Auditoria

        if not auditoria_id:
            return redirect('lista_auditorias')

        try:
            auditoria = Auditoria.objects.get(id=auditoria_id)
        except Auditoria.DoesNotExist:
            messages.error(request, "Auditoria não encontrada.")
            return redirect('lista_auditorias')

        form = self.form_class(request.POST, instance=auditoria)
        if form.is_valid():
            form.save()
            messages.success(request, f"Auditoria '{auditoria.nome}' atualizada com sucesso!")
            return redirect('lista_auditorias')

        contexto = {
            'form': form,
            'auditoria': auditoria,
            'auditoria_id': auditoria_id,
        }
        return render(request, self.template_name, contexto)


class DeleteAuditoriaView(View):
    """View for deleting audits.

    This view allows authorized users (Auditors) to delete
    existing audits. Displays confirmation page before deletion.

    Requires user authentication and appropriate permissions.
    """
    template_name = "ismsapp/deletar_auditoria.html"

    def _check_permission(self, user):
        """Check if user has permission to delete audits."""
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        return user_profile.actor_type == UserProfile.Actor.AUDITOR

    @method_decorator(login_required(login_url="login"))
    def get(self, request, auditoria_id=None, *args, **kwargs):
        """Display audit deletion confirmation page."""
        if not self._check_permission(request.user):
            return redirect('dashboard')

        from .models import Auditoria

        if not auditoria_id:
            return redirect('lista_auditorias')

        try:
            auditoria = Auditoria.objects.get(id=auditoria_id)
        except Auditoria.DoesNotExist:
            messages.error(request, "Auditoria não encontrada.")
            return redirect('lista_auditorias')

        contexto = {
            'auditoria': auditoria,
            'auditoria_id': auditoria_id,
        }
        return render(request, self.template_name, contexto)

    @method_decorator(login_required(login_url="login"))
    def post(self, request, auditoria_id=None, *args, **kwargs):
        """Handle audit deletion."""
        if not self._check_permission(request.user):
            return redirect('dashboard')

        from .models import Auditoria

        if not auditoria_id:
            return redirect('lista_auditorias')

        try:
            auditoria = Auditoria.objects.get(id=auditoria_id)
            audit_name = auditoria.nome
            auditoria.delete()
            messages.success(request, f"Auditoria '{audit_name}' deletada com sucesso!")
            return redirect('lista_auditorias')
        except Auditoria.DoesNotExist:
            messages.error(request, "Auditoria não encontrada.")
            return redirect('lista_auditorias')


# ============================================================================
# CONTROLE CRUD VIEWS
# ============================================================================

class CadastroControleView(View):
    """View for creating new security controls (Controles).

    This view allows authorized users (System Administrators and Security Auditors)
    to register new security controls with:
    - Control name/ID (e.g., "5.1 - Políticas de segurança")
    - Detailed description
    - One or more control categories (Preventivo, Detectivo, Corretivo)

    Only SISTEMA_ADMIN and AUDITOR roles can create controls.
    Requires user authentication.
    """
    template_name = "ismsapp/cadastro_controle.html"

    def _check_permission(self, user):
        """Check if user has permission to create controls."""
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        allowed_actors = [
            UserProfile.Actor.SISTEMA_ADMIN,
            UserProfile.Actor.AUDITOR
        ]
        return user_profile.actor_type in allowed_actors

    @method_decorator(login_required(login_url="login"))
    def get(self, request, *args, **kwargs):
        """Display control creation form."""
        if not self._check_permission(request.user):
            return redirect('dashboard')

        from .forms import CadastroControleForm

        form = CadastroControleForm()
        contexto = {
            'form': form,
            'page_title': 'Cadastro de Controle',
        }
        return render(request, self.template_name, contexto)

    @method_decorator(login_required(login_url="login"))
    def post(self, request, *args, **kwargs):
        """Handle control creation."""
        if not self._check_permission(request.user):
            return redirect('dashboard')

        from .forms import CadastroControleForm

        form = CadastroControleForm(request.POST)

        if form.is_valid():
            controle = form.save(commit=False)
            controle.save()

            # Handle ManyToMany categorias field
            categorias = form.cleaned_data.get('categorias', [])
            controle.categorias.set(categorias)

            messages.success(
                request,
                f"Controle '{controle.nome}' cadastrado com sucesso!"
            )
            return redirect('lista_controles')
        else:
            contexto = {
                'form': form,
                'page_title': 'Cadastro de Controle',
                'errors': form.errors,
            }
            return render(request, self.template_name, contexto)


class ReadControleView(View):
    """View for listing all security controls.

    This view allows authorized users to see all registered controls
    with their categories and descriptions. Includes pagination and
    optional filtering by control category.

    Only SISTEMA_ADMIN and AUDITOR roles can view controls.
    """
    template_name = "ismsapp/lista_controles.html"

    def _check_permission(self, user):
        """Check if user has permission to view controls."""
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        allowed_actors = [
            UserProfile.Actor.SISTEMA_ADMIN,
            UserProfile.Actor.AUDITOR
        ]
        return user_profile.actor_type in allowed_actors

    @method_decorator(login_required(login_url="login"))
    def get(self, request, *args, **kwargs):
        """Display list of controls."""
        if not self._check_permission(request.user):
            return redirect('dashboard')

        from .models import Controle, CategoriaControle
        from django.core.paginator import Paginator

        # Get filter parameters
        categoria_filter = request.GET.get('categoria')
        search_query = request.GET.get('search', '')

        # Base queryset
        controles = Controle.objects.all().prefetch_related('categorias').order_by('nome')

        # Apply filters
        if categoria_filter:
            try:
                categoria = CategoriaControle.objects.get(id=categoria_filter)
                controles = controles.filter(categorias=categoria)
            except CategoriaControle.DoesNotExist:
                pass

        if search_query:
            controles = controles.filter(
                nome__icontains=search_query
            ) | controles.filter(
                descricao__icontains=search_query
            )

        # Pagination
        paginator = Paginator(controles, 10)  # 10 controls per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Get all categories for filter dropdown
        categorias = CategoriaControle.objects.all().order_by('tipo')

        contexto = {
            'page_obj': page_obj,
            'controles': page_obj.object_list,
            'categorias': categorias,
            'selected_categoria': categoria_filter,
            'search_query': search_query,
            'page_title': 'Lista de Controles',
        }
        return render(request, self.template_name, contexto)


class UpdateControleView(View):
    """View for editing existing security controls.

    This view allows authorized users (System Administrators and Security Auditors)
    to update control details:
    - Name/ID
    - Description
    - Associated categories

    Only SISTEMA_ADMIN and AUDITOR roles can edit controls.
    """
    template_name = "ismsapp/editar_controle.html"

    def _check_permission(self, user):
        """Check if user has permission to edit controls."""
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        allowed_actors = [
            UserProfile.Actor.SISTEMA_ADMIN,
            UserProfile.Actor.AUDITOR
        ]
        return user_profile.actor_type in allowed_actors

    @method_decorator(login_required(login_url="login"))
    def get(self, request, controle_id=None, *args, **kwargs):
        """Display control editing form."""
        if not self._check_permission(request.user):
            return redirect('dashboard')

        from .models import Controle
        from .forms import CadastroControleForm

        if not controle_id:
            return redirect('lista_controles')

        try:
            controle = Controle.objects.get(id=controle_id)
        except Controle.DoesNotExist:
            messages.error(request, "Controle não encontrado.")
            return redirect('lista_controles')

        form = CadastroControleForm(instance=controle)
        contexto = {
            'form': form,
            'controle': controle,
            'controle_id': controle_id,
            'page_title': f'Editar Controle: {controle.nome}',
        }
        return render(request, self.template_name, contexto)

    @method_decorator(login_required(login_url="login"))
    def post(self, request, controle_id=None, *args, **kwargs):
        """Handle control update."""
        if not self._check_permission(request.user):
            return redirect('dashboard')

        from .models import Controle
        from .forms import CadastroControleForm

        if not controle_id:
            return redirect('lista_controles')

        try:
            controle = Controle.objects.get(id=controle_id)
        except Controle.DoesNotExist:
            messages.error(request, "Controle não encontrado.")
            return redirect('lista_controles')

        form = CadastroControleForm(request.POST, instance=controle)

        if form.is_valid():
            controle = form.save(commit=False)
            controle.save()

            # Handle ManyToMany categorias field
            categorias = form.cleaned_data.get('categorias', [])
            controle.categorias.set(categorias)

            messages.success(
                request,
                f"Controle '{controle.nome}' atualizado com sucesso!"
            )
            return redirect('lista_controles')
        else:
            contexto = {
                'form': form,
                'controle': controle,
                'controle_id': controle_id,
                'page_title': f'Editar Controle: {controle.nome}',
                'errors': form.errors,
            }
            return render(request, self.template_name, contexto)


class DeleteControleView(View):
    """View for deleting security controls.

    This view allows authorized users (System Administrators and Security Auditors)
    to delete existing controls. Displays confirmation before deletion.

    Only SISTEMA_ADMIN and AUDITOR roles can delete controls.
    """
    template_name = "ismsapp/deletar_controle.html"

    def _check_permission(self, user):
        """Check if user has permission to delete controls."""
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        allowed_actors = [
            UserProfile.Actor.SISTEMA_ADMIN,
            UserProfile.Actor.AUDITOR
        ]
        return user_profile.actor_type in allowed_actors

    @method_decorator(login_required(login_url="login"))
    def get(self, request, controle_id=None, *args, **kwargs):
        """Display control deletion confirmation page."""
        if not self._check_permission(request.user):
            return redirect('dashboard')

        from .models import Controle

        if not controle_id:
            return redirect('lista_controles')

        try:
            controle = Controle.objects.get(id=controle_id)
        except Controle.DoesNotExist:
            messages.error(request, "Controle não encontrado.")
            return redirect('lista_controles')

        # Get treatments using this control
        tratamentos = controle.tratamentos.all()

        contexto = {
            'controle': controle,
            'controle_id': controle_id,
            'tratamentos': tratamentos,
            'page_title': f'Deletar Controle: {controle.nome}',
        }
        return render(request, self.template_name, contexto)

    @method_decorator(login_required(login_url="login"))
    def post(self, request, controle_id=None, *args, **kwargs):
        """Handle control deletion."""
        if not self._check_permission(request.user):
            return redirect('dashboard')

        from .models import Controle

        if not controle_id:
            return redirect('lista_controles')

        try:
            controle = Controle.objects.get(id=controle_id)
            controle_name = controle.nome
            controle.delete()
            messages.success(
                request,
                f"Controle '{controle_name}' deletado com sucesso!"
            )
            return redirect('lista_controles')
        except Controle.DoesNotExist:
            messages.error(request, "Controle não encontrado.")
            return redirect('lista_controles')


class CalculateControlReductionsView(View):
    """AJAX endpoint for calculating risk reductions based on selected control types.

    This view implements the HYBRID approach for risk reduction calculation.
    It receives selected control IDs and returns the expected probability and
    consequence reduction percentages based on the control categories
    (Preventivo, Detectivo, Corretivo).

    Request:
    - POST to /api/calculate-control-reductions/
    - Content-Type: application/json
    - Data: {
        "risco_id": <int>,  # The risk ID (optional, for context)
        "controle_ids": "<comma-separated IDs>"
      }

    Response:
    - JSON with:
      - prob_reduction: <int> percentage for probability reduction
      - impact_reduction: <int> percentage for consequence reduction
      - breakdown: <array> of control type effectiveness
      - has_controls: <boolean> if relevant controls found
    """

    @method_decorator(login_required(login_url="login"))
    def post(self, request, *args, **kwargs):
        """Handle AJAX POST request for control reduction calculation."""
        try:
            import json
            from .models import Controle

            # Parse JSON request body
            data = json.loads(request.body)
            controle_ids_str = data.get('controle_ids', '')

            if not controle_ids_str:
                return JsonResponse({
                    'prob_reduction': 0,
                    'impact_reduction': 0,
                    'breakdown': [],
                    'has_controls': False,
                    'error': 'No controls provided'
                })

            # Parse control IDs
            controle_ids = [int(id.strip()) for id in controle_ids_str.split(',') if id.strip()]

            if not controle_ids:
                return JsonResponse({
                    'prob_reduction': 0,
                    'impact_reduction': 0,
                    'breakdown': [],
                    'has_controls': False,
                    'error': 'Invalid control IDs'
                })

            # Get selected controls
            controles = Controle.objects.filter(id__in=controle_ids).prefetch_related('categorias')

            if not controles.exists():
                return JsonResponse({
                    'prob_reduction': 0,
                    'impact_reduction': 0,
                    'breakdown': [],
                    'has_controls': False,
                    'error': 'No controls found'
                })

            # Calculate reductions using TratamentoRiscoView's method
            tratamento_view = TratamentoRiscoView()
            results = tratamento_view._calculate_control_reductions(controles)

            return JsonResponse(results)

        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON',
                'prob_reduction': 0,
                'impact_reduction': 0,
                'breakdown': [],
                'has_controls': False
            }, status=400)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'error': str(e),
                'prob_reduction': 0,
                'impact_reduction': 0,
                'breakdown': [],
                'has_controls': False
            }, status=500)
            return redirect('lista_auditorias')