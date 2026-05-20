from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.http.response import HttpResponseRedirect, JsonResponse
from django.urls.base import reverse_lazy, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from urllib.parse import urlencode
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

    def post(self, request, *args, **kwargs):
        """Allow logout via POST (used by the header logout form)."""
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

        ativos_module_count = sum([
            pode_cadastrar_categorias_de_ativos,
            pode_cadastrar_ativos,
            pode_cadastrar_ativos,
            pode_criar_criterios_de_valoracao_dos_ativos or pode_analisar_valoracao_dos_ativos,
        ])
        controles_module_count = 2 if pode_gerenciar_controles else 0
        riscos_module_count = sum([
            pode_criar_criterios_para_avaliacao_dos_riscos,
            pode_identificar_riscos,
            pode_identificar_riscos,
            pode_analisar_riscos,
            pode_avaliar_riscos,
            pode_tratar_riscos,
        ])
        ameacas_module_count = 2 if pode_detectar_ameacas else 0
        vulnerabilidades_module_count = 2 if pode_gerenciar_vulnerabilidades else 0
        incidentes_module_count = 2 if pode_gestionar_incidentes_de_seguranca else 0
        auditorias_module_count = 2 if pode_registrar_auditorias else 0

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
            "ativos_module_count": ativos_module_count,
            "controles_module_count": controles_module_count,
            "riscos_module_count": riscos_module_count,
            "ameacas_module_count": ameacas_module_count,
            "vulnerabilidades_module_count": vulnerabilidades_module_count,
            "incidentes_module_count": incidentes_module_count,
            "auditorias_module_count": auditorias_module_count,
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
            from django.contrib import messages
            messages.success(request, 'Ativo cadastrado com sucesso!')
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
        sort = request.GET.get('sort', 'nome')
        direction = request.GET.get('direction', 'asc')

        sort_map = {
            'id': 'id',
            'nome': 'nome',
            'categoria': 'categoria__nome',
        }
        sort_field = sort_map.get(sort, 'nome')
        ordering = sort_field if direction != 'desc' else f'-{sort_field}'

        ativos = Ativo.objects.select_related('categoria').all().order_by(ordering)

        if search_query:
            ativos = ativos.filter(
                Q(nome__icontains=search_query) |
                Q(categoria__nome__icontains=search_query)
            )

        paginator = Paginator(ativos, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        query_params = {
            'search': search_query,
            'sort': sort,
            'direction': direction,
        }
        query_string = urlencode({key: value for key, value in query_params.items() if value})

        def sort_query(column_name):
            next_direction = 'desc' if sort == column_name and direction != 'desc' else 'asc'
            params = query_params | {'sort': column_name, 'direction': next_direction}
            return urlencode({key: value for key, value in params.items() if value})

        # Check edit/delete permissions
        user_profile = getattr(request.user, 'profile', None)
        pode_editar_deletar = user_profile and user_profile.actor_type in [
            UserProfile.Actor.SISTEMA_ADMIN,
            UserProfile.Actor.AUDITOR
        ]

        contexto = {
            'ativos': page_obj,
            'page_obj': page_obj,
            'paginator': paginator,
            'total_ativos': paginator.count,
            'pode_editar_deletar': pode_editar_deletar,
            'search_query': search_query,
            'sort': sort,
            'direction': direction,
            'query_string': query_string,
            'sort_id_query': sort_query('id'),
            'sort_nome_query': sort_query('nome'),
            'sort_categoria_query': sort_query('categoria'),
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
            messages.success(request, 'Ativo deletado com sucesso!')
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
        Risks AT OR BELOW this threshold are acceptable without treatment.

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
        """Determine if a risk value is within the accepted risk appetite.

        A risk is acceptable if its numeric value is STRICTLY LESS THAN
        the acceptance level. Risks equal to the threshold are considered
        borderline and require monitoring — they are NOT automatically accepted.

        This avoids the contradiction of a risk being both acceptable and
        requiring treatment when it falls exactly on the threshold.
        """
        try:
            return float(risk_value) < acceptance_level

        except (TypeError, ValueError):
            return False

    def _get_suggestions_for_risk(self, risk_level, risk_value=None, acceptance_level=None):
        """Get treatment suggestions based on risk level.

        Maps risk levels to appropriate treatment strategies:

        - Baixo (Low):    Tolerável — Aceitar sem restrições
        - Médio (Medium): Tolerável com monitoramento — Aceitar com revisão periódica
        - Alto (High):    Não tolerável — Tratar (modificar, evitar, compartilhar)
        - Crítico (Critical): Não tolerável — Ação imediata obrigatória

        Args:
            risk_level: The category string of the risk level.
            risk_value: Optional numeric value to detect borderline risks.
            acceptance_level: Optional threshold to detect borderline risks.

        Returns a dict with structured suggestions for the risk level.
        """
        risk_level_lower = risk_level.lower() if risk_level else ""

        # Detect borderline: risk value exactly equals the acceptance threshold
        is_borderline = (
            risk_value is not None
            and acceptance_level is not None
            and float(risk_value) == float(acceptance_level)
        )

        suggestions = {
            'nivel_risco': risk_level,
            'recomendacoes': [],
            'cor_categoria': 'neutral',
            'icone': 'info',
            'borderline': is_borderline,
        }

        if 'baixo' in risk_level_lower:
            suggestions.update({
                'cor_categoria': 'baixo',
                'icone': 'check-circle',
                'recomendacoes': [
                    {
                        'titulo': 'Aceitar',
                        'tipo': 'aceitar',
                        'descricao': (
                            'Risco tolerável dentro do apetite organizacional. '
                            'Nenhuma ação imediata é necessária.'
                        ),
                        'acoes': [
                            'Documentar a decisão de aceitação no registro de riscos',
                            'Revisar o risco na próxima avaliação periódica',
                            'Manter controles preventivos existentes ativos',
                        ]
                    }
                ]
            })

        elif 'médio' in risk_level_lower or 'medio' in risk_level_lower:
            suggestions.update({
                'cor_categoria': 'medio',
                'icone': 'alert-circle',
                'recomendacoes': [
                    {
                        'titulo': 'Aceitar com Monitoramento',
                        'tipo': 'aceitar',
                        'descricao': (
                            'Risco tolerável, porém com probabilidade razoável de impacto moderado. '
                            'Aceitar condicionado a revisão periódica e monitoramento contínuo.'
                        ),
                        'acoes': [
                            'Registrar formalmente a aceitação com justificativa',
                            'Definir indicadores de monitoramento para este risco',
                            'Estabelecer frequência de revisão',
                            'Verificar se os controles existentes ainda são eficazes',
                        ]
                    }
                ]
            })
            if is_borderline:
                suggestions['recomendacoes'].append({
                    'titulo': 'Alternativa: Tratar',
                    'tipo': 'tratar',
                    'descricao': (
                        'Este risco está exatamente no limite do apetite definido. '
                        'Considere tratamento preventivo para reduzir a exposição.'
                    ),
                    'acoes': [
                        'Implementar controles adicionais para reduzir probabilidade',
                        'Revisar o impacto esperado com a área responsável',
                    ]
                })

        elif 'alto' in risk_level_lower:
            suggestions.update({
                'cor_categoria': 'alto',
                'icone': 'alert-triangle',
                'recomendacoes': [
                    {
                        'titulo': 'Tratar — Modificar',
                        'tipo': 'tratar',
                        'descricao': (
                            'Implementar ou fortalecer controles para reduzir a probabilidade '
                            'ou o impacto do risco a um nível aceitável.'
                        ),
                        'acoes': [
                            'Identificar e implementar controles técnicos ou administrativos',
                            'Definir responsável e prazo para implementação',
                            'Estabelecer plano de ação com marcos mensuráveis',
                            'Monitorar a eficácia dos controles após implementação',
                        ]
                    },
                    {
                        'titulo': 'Tratar — Evitar',
                        'tipo': 'tratar',
                        'descricao': (
                            'Eliminar a atividade ou processo que origina o risco, '
                            'caso o custo-benefício do tratamento não seja viável.'
                        ),
                        'acoes': [
                            'Avaliar viabilidade de descontinuar a atividade de risco',
                            'Mapear impactos operacionais da eliminação',
                            'Propor alternativas ao processo de origem',
                        ]
                    },
                    {
                        'titulo': 'Tratar — Compartilhar / Transferir',
                        'tipo': 'tratar',
                        'descricao': (
                            'Transferir parte ou toda a exposição ao risco para terceiros, '
                            'como seguradoras ou fornecedores de serviços gerenciados.'
                        ),
                        'acoes': [
                            'Avaliar contratação ou revisão de apólice de seguro',
                            'Revisar cláusulas de responsabilidade em contratos com fornecedores',
                            'Considerar outsourcing de atividades de alto risco',
                        ]
                    },
                ]
            })

        elif 'crítico' in risk_level_lower or 'critico' in risk_level_lower:
            suggestions.update({
                'cor_categoria': 'critico',
                'icone': 'alert-triangle',
                'recomendacoes': [
                    {
                        'titulo': 'Ação Imediata — Modificar / Mitigar',
                        'tipo': 'tratar',
                        'descricao': (
                            'Risco crítico: probabilidade e impacto ultrapassam os critérios definidos. '
                            'Controles devem ser implementados imediatamente, sem aguardar o próximo ciclo de revisão.'
                        ),
                        'acoes': [
                            'Escalar imediatamente para a gestão',
                            'Acionar plano de resposta a incidentes se o risco já se materializou',
                            'Implementar controles emergenciais',
                            'Definir plano de mitigação formal',
                            'Monitorar diariamente até que o risco seja reduzido a nível aceitável',
                        ]
                    },
                    {
                        'titulo': 'Evitar — Suspender a Atividade',
                        'tipo': 'tratar',
                        'descricao': (
                            'Se controles imediatos não forem viáveis, considere suspender '
                            'temporariamente a atividade que origina o risco até que o tratamento esteja em vigor.'
                        ),
                        'acoes': [
                            'Avaliar suspensão temporária da atividade ou sistema afetado',
                            'Comunicar partes interessadas sobre a interrupção e o prazo previsto',
                            'Documentar a decisão e obter aprovação da gestão',
                        ]
                    },
                    {
                        'titulo': 'Compartilhar — Transferência de Emergência',
                        'tipo': 'tratar',
                        'descricao': (
                            'Acionar mecanismos de transferência de risco já existentes '
                            'ou negociar cobertura emergencial com parceiros e seguradoras.'
                        ),
                        'acoes': [
                            'Verificar cobertura atual de seguro cibernético / operacional',
                            'Notificar seguradora se o risco já se materializou',
                            'Acionar cláusulas contratuais de responsabilidade com fornecedores',
                        ]
                    },
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

        risco_selecionado_aceitavel = None
        if risco_selecionado:
            risco_selecionado_aceitavel = self._is_risk_acceptable(
                risco_selecionado.valor_risco_inerente,
                acceptance_level
            )

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
            sugestoes = self._get_suggestions_for_risk(
                risco_selecionado.nivel_inerente.categoria,
                risk_value=risco_selecionado.valor_risco_inerente,
                acceptance_level=acceptance_level,
            )

        contexto = {
            'riscos': riscos_para_apresentacao,
            'risco_selecionado': risco_selecionado,
            'criterio_avaliacao': criterio_avaliacao,
            'apetite_risco': criterio_avaliacao.get_apetite_risco_display() if criterio_avaliacao else 'Não Definido',
            'acceptance_level': acceptance_level,
            'sugestoes': sugestoes,
            'risco_selecionado_aceitavel': risco_selecionado_aceitavel,
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

    # Permission

    def _check_permission(self, user):
        """Check if user has permission to create risk treatments."""
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        allowed_actors = [
            UserProfile.Actor.AUDITOR,
            UserProfile.Actor.ANALISTA,
        ]
        return user_profile.actor_type in allowed_actors

    # Residual risk calculation

    def _calculate_residual_risk(self, risk, reducao_prob, reducao_impacto):
        """Calculate residual risk after applying treatment reductions.

        Applies percentage reductions to the *inherent* probability and
        consequence weights, then multiplies them to get the residual risk
        value — the same formula used for the inherent risk in UC-07.

        The reduction percentages are clamped to [0, 95] so a treatment can
        never claim to eliminate 100% of a risk (that would be "Evitar", not
        a reduction).

        Returns:
            (valor_residual, nivel_residual, breakdown_dict) or
            (None, None, None) if the risk lacks inherent data.
        """
        from .models import Nivel
        from decimal import Decimal

        if not risk.probabilidade_inerente or not risk.consequencia_inerente:
            return None, None, None

        # Clamp reductions to a realistic ceiling
        _reducao_prob = min(float(reducao_prob), 95.0)
        _reducao_impacto = min(float(reducao_impacto), 95.0)

        prob_original = float(risk.probabilidade_inerente.peso)
        cons_original = float(risk.consequencia_inerente.peso)

        prob_residual = prob_original * (1.0 - _reducao_prob / 100.0)
        cons_residual = cons_original * (1.0 - _reducao_impacto / 100.0)

        valor_residual = prob_residual * cons_residual

        # Map the numeric residual value to the closest Nivel (RESIDUAL type),
        # picking the first level whose peso >= the calculated value.
        # Falls back to the highest level if none match (risk is off the top
        # of the defined scale).
        nivel_candidates = Nivel.objects.filter(
            tipo=Nivel.Tipo.RESIDUAL
        ).order_by('peso')

        nivel_residual = None
        if nivel_candidates.exists():
            for nivel in nivel_candidates:
                if float(nivel.peso) >= valor_residual:
                    nivel_residual = nivel
                    break
            if nivel_residual is None:
                nivel_residual = nivel_candidates.last()

        breakdown = {
            'prob_original': prob_original,
            'prob_residual': round(prob_residual, 4),
            'prob_reducao_aplicada': round(_reducao_prob, 1),
            'cons_original': cons_original,
            'cons_residual': round(cons_residual, 4),
            'cons_reducao_aplicada': round(_reducao_impacto, 1),
            'valor_inerente': round(prob_original * cons_original, 4),
            'valor_residual': round(valor_residual, 4),
        }

        return Decimal(str(round(valor_residual, 4))), nivel_residual, breakdown

    # Control-based reduction estimation

    # Control effectiveness table.
    # Each entry defines per-control probability and consequence reduction
    # percentages and a diminishing-returns cap for the whole category.
    # Values are conservative by design — over-estimating residual risk is
    # safer than under-estimating it.
    _CONTROL_EFFECTIVENESS = {
        'preventivo': {
            'prob_per_control': 20,     # reduces probability only
            'cons_per_control': 0,
            'prob_cap': 60,             # max contribution from this category
            'cons_cap': 0,
            'label': 'Preventivo',
            'reduces_prob': True,
            'reduces_cons': False,
            'exemplo': 'Ex: controle de acesso, firewall, autenticação MFA',
        },
        'detectivo': {
            'prob_per_control': 10,     # catches threats early → less probability
            'cons_per_control': 15,     # early detection limits impact
            'prob_cap': 30,
            'cons_cap': 45,
            'label': 'Detectivo',
            'reduces_prob': True,
            'reduces_cons': True,
            'exemplo': 'Ex: IDS/IPS, monitoramento SIEM, auditoria contínua',
        },
        'corretivo': {
            'prob_per_control': 0,      # does not prevent occurrence
            'cons_per_control': 25,     # limits damage after the fact
            'prob_cap': 0,
            'cons_cap': 60,
            'label': 'Corretivo / Contingência',
            'reduces_prob': False,
            'reduces_cons': True,
            'exemplo': 'Ex: backup, plano de recuperação, redundância, BCP/DR',
        },
    }

    def _calculate_control_reductions(self, controles):
        """Estimate probability and consequence reductions from a set of controls.

        Uses a diminishing-returns model per category: each additional control
        of the same type adds progressively less until the category cap is
        reached.  Combined reductions across categories are bounded at 95% to
        preserve the principle that residual risk is never zero.

        Returns a dict with:
            prob_reduction (float): aggregate probability reduction %
            impact_reduction (float): aggregate consequence reduction %
            breakdown (list): per-category contribution details
            has_controls (bool): whether any contributing controls were found
            warnings (list): advisory messages (e.g. capped categories)
        """
        if not controles:
            return {
                'prob_reduction': 0,
                'impact_reduction': 0,
                'breakdown': [],
                'has_controls': False,
                'warnings': [],
            }

        # Bucket controls by category keyword
        buckets = {k: [] for k in self._CONTROL_EFFECTIVENESS}

        for controle in controles:
            matched = False
            for categoria in controle.categorias.all():
                tipo_lower = categoria.tipo.lower()
                for key in self._CONTROL_EFFECTIVENESS:
                    if key in tipo_lower:
                        buckets[key].append(controle)
                        matched = True
                        break
                if matched:
                    break

        prob_total = 0.0
        cons_total = 0.0
        breakdown = []
        warnings = []

        for key, controls_in_bucket in buckets.items():
            if not controls_in_bucket:
                continue

            eff = self._CONTROL_EFFECTIVENESS[key]
            n = len(controls_in_bucket)

            # Diminishing returns: contribution of the k-th control is
            # per_control * (0.8 ** (k-1))  →  roughly geometric decay.
            def _diminishing(per_control, cap):
                total = 0.0
                for k in range(n):
                    total += per_control * (0.8 ** k)
                return min(total, float(cap))

            cat_prob = _diminishing(eff['prob_per_control'], eff['prob_cap'])
            cat_cons = _diminishing(eff['cons_per_control'], eff['cons_cap'])

            # Warn when the category cap was the binding constraint
            raw_prob = sum(eff['prob_per_control'] * (0.8 ** k) for k in range(n))
            raw_cons = sum(eff['cons_per_control'] * (0.8 ** k) for k in range(n))
            if raw_prob > eff['prob_cap'] and eff['prob_cap'] > 0:
                warnings.append(
                    f"Controles {eff['label']}: contribuição máxima de "
                    f"{eff['prob_cap']}% de redução de probabilidade atingida "
                    f"({n} controles). Controles adicionais deste tipo não aumentam "
                    f"a redução estimada."
                )
            if raw_cons > eff['cons_cap'] and eff['cons_cap'] > 0:
                warnings.append(
                    f"Controles {eff['label']}: contribuição máxima de "
                    f"{eff['cons_cap']}% de redução de consequência atingida."
                )

            prob_total += cat_prob
            cons_total += cat_cons

            breakdown.append({
                'tipo': eff['label'],
                'quantidade': n,
                'reduces_prob': eff['reduces_prob'],
                'reduces_cons': eff['reduces_cons'],
                'prob_contribution': round(cat_prob, 1),
                'cons_contribution': round(cat_cons, 1),
                'exemplo': eff['exemplo'],
            })

        # Global cap — residual risk can never be reduced to zero
        _MAX = 95.0
        if prob_total > _MAX:
            warnings.append(
                f"Redução total de probabilidade limitada a {_MAX}% "
                f"(valor calculado: {prob_total:.1f}%)."
            )
        if cons_total > _MAX:
            warnings.append(
                f"Redução total de consequência limitada a {_MAX}% "
                f"(valor calculado: {cons_total:.1f}%)."
            )

        return {
            'prob_reduction': round(min(prob_total, _MAX), 1),
            'impact_reduction': round(min(cons_total, _MAX), 1),
            'breakdown': breakdown,
            'has_controls': bool(breakdown),
            'warnings': warnings,
        }

    # Treatment suggestions

    def _get_suggestions_for_risk(self, risk_level, risk_value=None, acceptance_level=None):
        """Get treatment suggestions based on risk level.

        Mirrors the rich suggestion logic in AvaliacaoRiscoView so both views
        present consistent guidance.  Includes borderline detection when
        risk_value and acceptance_level are supplied.

        Args:
            risk_level: Category string from Nivel.categoria.
            risk_value: Optional numeric risk value for borderline detection.
            acceptance_level: Optional acceptance threshold for borderline detection.

        Returns:
            dict with keys: nivel_risco, cor_categoria, icone, borderline,
            recomendacoes (list of dicts with titulo, tipo, descricao, acoes).
        """
        if not risk_level:
            return None

        risk_level_lower = str(risk_level).strip().lower()

        is_borderline = (
            risk_value is not None
            and acceptance_level is not None
            and float(risk_value) == float(acceptance_level)
        )

        suggestions = {
            'nivel_risco': risk_level,
            'recomendacoes': [],
            'cor_categoria': 'neutral',
            'icone': 'info',
            'borderline': is_borderline,
        }

        if 'baixo' in risk_level_lower:
            suggestions.update({
                'cor_categoria': 'baixo',
                'icone': 'check-circle',
                'recomendacoes': [
                    {
                        'titulo': 'Aceitar',
                        'tipo': 'aceitar',
                        'descricao': (
                            'Risco tolerável dentro do apetite organizacional. '
                            'Nenhuma ação imediata é necessária.'
                        ),
                        'acoes': [
                            'Documentar a decisão de aceitação no registro de riscos',
                            'Revisar o risco na próxima avaliação periódica',
                            'Manter controles preventivos existentes ativos',
                        ],
                    }
                ],
            })

        elif 'moderado' in risk_level_lower or 'médio' in risk_level_lower or 'medio' in risk_level_lower:
            suggestions.update({
                'cor_categoria': 'medio',
                'icone': 'alert-circle',
                'recomendacoes': [
                    {
                        'titulo': 'Aceitar com Monitoramento',
                        'tipo': 'aceitar',
                        'descricao': (
                            'Risco tolerável, porém com probabilidade razoável de impacto moderado. '
                            'Aceitar condicionado a revisão periódica e monitoramento contínuo.'
                        ),
                        'acoes': [
                            'Registrar formalmente a aceitação com justificativa',
                            'Definir indicadores de monitoramento (KRIs) para este risco',
                            'Estabelecer frequência de revisão (recomendado: trimestral)',
                            'Verificar se os controles existentes ainda são eficazes',
                        ],
                    }
                ],
            })
            if is_borderline:
                suggestions['recomendacoes'].append({
                    'titulo': 'Alternativa: Tratar',
                    'tipo': 'tratar',
                    'descricao': (
                        'Este risco está exatamente no limite do apetite definido. '
                        'Considere tratamento preventivo para reduzir a exposição.'
                    ),
                    'acoes': [
                        'Implementar controles adicionais para reduzir probabilidade',
                        'Revisar o impacto esperado com a área responsável',
                    ],
                })

        elif 'alto' in risk_level_lower:
            suggestions.update({
                'cor_categoria': 'alto',
                'icone': 'alert-triangle',
                'recomendacoes': [
                    {
                        'titulo': 'Tratar — Modificar',
                        'tipo': 'tratar',
                        'descricao': (
                            'Implementar ou fortalecer controles para reduzir a probabilidade '
                            'ou o impacto do risco a um nível aceitável.'
                        ),
                        'acoes': [
                            'Identificar e implementar controles técnicos ou administrativos',
                            'Definir responsável (owner) e prazo para implementação',
                            'Estabelecer plano de ação com marcos mensuráveis',
                            'Monitorar a eficácia dos controles após implementação',
                        ],
                    },
                    {
                        'titulo': 'Tratar — Evitar',
                        'tipo': 'tratar',
                        'descricao': (
                            'Eliminar a atividade ou processo que origina o risco, '
                            'caso o custo-benefício do tratamento não seja viável.'
                        ),
                        'acoes': [
                            'Avaliar viabilidade de descontinuar a atividade de risco',
                            'Mapear impactos operacionais da eliminação',
                            'Propor alternativas ao processo de origem',
                        ],
                    },
                    {
                        'titulo': 'Tratar — Compartilhar / Transferir',
                        'tipo': 'tratar',
                        'descricao': (
                            'Transferir parte ou toda a exposição ao risco para terceiros, '
                            'como seguradoras ou fornecedores de serviços gerenciados.'
                        ),
                        'acoes': [
                            'Avaliar contratação ou revisão de apólice de seguro',
                            'Revisar cláusulas de responsabilidade em contratos com fornecedores',
                            'Considerar outsourcing de atividades de alto risco',
                        ],
                    },
                ],
            })

        elif 'crítico' in risk_level_lower or 'critico' in risk_level_lower:
            suggestions.update({
                'cor_categoria': 'critico',
                'icone': 'alert-triangle',
                'recomendacoes': [
                    {
                        'titulo': 'Ação Imediata — Modificar / Mitigar',
                        'tipo': 'tratar',
                        'descricao': (
                            'Risco crítico: probabilidade e impacto ultrapassam os critérios definidos. '
                            'Controles devem ser implementados imediatamente, sem aguardar o próximo ciclo de revisão.'
                        ),
                        'acoes': [
                            'Escalar imediatamente para a gestão e o CISO / responsável pela SI',
                            'Acionar plano de resposta a incidentes se o risco já se materializou',
                            'Implementar controles emergenciais (técnicos e processuais) em até 48h',
                            'Definir plano de mitigação formal com prazo máximo de 30 dias',
                            'Monitorar diariamente até que o risco seja reduzido a nível aceitável',
                        ],
                    },
                    {
                        'titulo': 'Evitar — Suspender a Atividade',
                        'tipo': 'tratar',
                        'descricao': (
                            'Se controles imediatos não forem viáveis, considere suspender '
                            'temporariamente a atividade que origina o risco até que o tratamento esteja em vigor.'
                        ),
                        'acoes': [
                            'Avaliar suspensão temporária da atividade ou sistema afetado',
                            'Comunicar partes interessadas sobre a interrupção e o prazo previsto',
                            'Documentar a decisão e obter aprovação da gestão',
                        ],
                    },
                    {
                        'titulo': 'Compartilhar — Transferência de Emergência',
                        'tipo': 'tratar',
                        'descricao': (
                            'Acionar mecanismos de transferência de risco já existentes '
                            'ou negociar cobertura emergencial com parceiros e seguradoras.'
                        ),
                        'acoes': [
                            'Verificar cobertura atual de seguro cibernético / operacional',
                            'Notificar seguradora se o risco já se materializou',
                            'Acionar cláusulas contratuais de responsabilidade com fornecedores',
                        ],
                    },
                ],
            })

        return suggestions if suggestions['recomendacoes'] else None

    # GET

    @method_decorator(login_required(login_url="login"))
    def get(self, request, *args, **kwargs):
        """Display treatment form or list of risks requiring treatment."""

        if not self._check_permission(request.user):
            messages.error(request, "Você não tem permissão para acessar esta página.")
            return redirect('dashboard')

        from .models import Risco, CriterioAvaliacaoRisco

        risco_id = request.GET.get('risco_id')

        # Resolve the acceptance threshold so suggestions can flag borderline risks
        try:
            criterio_avaliacao = CriterioAvaliacaoRisco.objects.first()
        except Exception:
            criterio_avaliacao = None

        acceptance_level = self._get_acceptance_level(criterio_avaliacao) if criterio_avaliacao else 12

        risco_selecionado = None
        if risco_id:
            try:
                risco_selecionado = Risco.objects.select_related(
                    'ativo',
                    'nivel_inerente',
                    'probabilidade_inerente',
                    'consequencia_inerente',
                    'nivel_residual',
                    'probabilidade_residual',
                    'consequencia_residual',
                ).get(id=risco_id)
            except Risco.DoesNotExist:
                messages.error(request, "Risco não encontrado.")

        # Risks eligible for treatment: those not yet fully accepted
        from django.db.models import Q
        riscos_para_tratar = Risco.objects.exclude(
            tratamentos__aceito=True
        ).select_related(
            'ativo',
            'nivel_inerente',
            'consequencia_inerente',
            'probabilidade_inerente',
        ).distinct()

        # Suggestions for the selected risk
        sugestoes = None
        if risco_selecionado and risco_selecionado.nivel_inerente:
            sugestoes = self._get_suggestions_for_risk(
                risco_selecionado.nivel_inerente.categoria,
                risk_value=risco_selecionado.valor_risco_inerente,
                acceptance_level=acceptance_level,
            )

        # Pre-populate form and derive control reductions from any existing treatment
        form_initial = {}
        control_reductions = None
        tratamento_existente = None
        residual_preview = None

        if risco_selecionado:
            tratamentos = risco_selecionado.tratamentos.order_by('-id')
            if tratamentos.exists():
                tratamento_existente = tratamentos.first()
                form_initial = {
                    'nome': tratamento_existente.nome,
                    'tipo_tratamento': tratamento_existente.tipo_tratamento,
                    'descricao': tratamento_existente.descricao,
                    'reducao_probabilidade': tratamento_existente.reducao_probabilidade,
                    'reducao_impacto': tratamento_existente.reducao_impacto,
                    'controles': tratamento_existente.controles.all(),
                }

                controles = tratamento_existente.controles.all()
                if controles.exists():
                    control_reductions = self._calculate_control_reductions(controles)

                    # Show a live residual preview based on existing treatment
                    valor_res, nivel_res, breakdown = self._calculate_residual_risk(
                        risco_selecionado,
                        tratamento_existente.reducao_probabilidade,
                        tratamento_existente.reducao_impacto,
                    )
                    if valor_res is not None:
                        residual_preview = {
                            'valor': valor_res,
                            'nivel': nivel_res,
                            'breakdown': breakdown,
                            'aceitavel': float(valor_res) < acceptance_level,
                        }

        contexto = {
            'riscos_para_tratar': riscos_para_tratar,
            'risco_selecionado': risco_selecionado,
            'form': self.form_class(initial=form_initial),
            'sugestoes': sugestoes,
            'control_reductions': control_reductions,
            'tratamento_existente': tratamento_existente,
            'residual_preview': residual_preview,
            'acceptance_level': acceptance_level,
            'criterio_avaliacao': criterio_avaliacao,
            'apetite_risco': criterio_avaliacao.get_apetite_risco_display() if criterio_avaliacao else 'Não Definido',
        }

        return render(request, self.template_name, contexto)

    # POST

    @method_decorator(login_required(login_url="login"))
    def post(self, request, *args, **kwargs):
        """Process risk treatment plan creation or update."""

        if not self._check_permission(request.user):
            messages.error(request, "Você não tem permissão para acessar esta página.")
            return redirect('dashboard')

        from .models import Risco, Tratamento, CriterioAvaliacaoRisco

        form = self.form_class(request.POST)

        if not form.is_valid():
            messages.error(request, "Formulário inválido. Verifique os dados inseridos.")
            risco_id = request.POST.get('risco_id')
            contexto = {
                'form': form,
                'risco_selecionado': Risco.objects.filter(id=risco_id).first() if risco_id else None,
                'riscos_para_tratar': Risco.objects.exclude(tratamentos__aceito=True).distinct(),
            }
            return render(request, self.template_name, contexto)

        try:
            risco_id = request.POST.get('risco_id')
            risco = Risco.objects.select_related(
                'probabilidade_inerente',
                'consequencia_inerente',
            ).get(id=risco_id)

            nome = form.cleaned_data['nome']
            tipo_tratamento = form.cleaned_data['tipo_tratamento']
            descricao = form.cleaned_data['descricao']
            reducao_prob = float(form.cleaned_data.get('reducao_probabilidade') or 0)
            reducao_impacto = float(form.cleaned_data.get('reducao_impacto') or 0)
            controles = form.cleaned_data.get('controles', [])

            # Upsert treatment
            tratamentos_existentes = risco.tratamentos.order_by('-id')

            if tratamentos_existentes.exists():
                tratamento = tratamentos_existentes.first()
                tratamento.nome = nome
                tratamento.tipo_tratamento = tipo_tratamento
                tratamento.descricao = descricao
                tratamento.reducao_probabilidade = reducao_prob
                tratamento.reducao_impacto = reducao_impacto
                tratamento.save()
                tratamento.controles.set(controles if controles else [])
                action_message = "atualizado"
            else:
                tratamento = Tratamento.objects.create(
                    nome=nome,
                    tipo_tratamento=tipo_tratamento,
                    descricao=descricao,
                    reducao_probabilidade=reducao_prob,
                    reducao_impacto=reducao_impacto,
                )
                if controles:
                    tratamento.controles.set(controles)
                risco.tratamentos.add(tratamento)
                action_message = "criado"

            # Calculate and persist residual risk
            valor_residual, nivel_residual, breakdown = self._calculate_residual_risk(
                risco, reducao_prob, reducao_impacto
            )

            if valor_residual is not None:
                risco.valor_risco_residual = valor_residual
                risco.nivel_residual = nivel_residual

                # Find the Probabilidade and Consequencia records whose peso
                # most closely matches the calculated residual weights so the
                # risk matrix can reflect the new position accurately.
                from .models import Probabilidade, Consequencia

                prob_residual_peso = breakdown['prob_residual']
                cons_residual_peso = breakdown['cons_residual']

                # Nearest Probabilidade by absolute distance on peso
                prob_residual_obj = (
                    Probabilidade.objects
                    .extra(
                        select={'dist': 'ABS(peso - %s)'},
                        select_params=[prob_residual_peso],
                    )
                    .order_by('dist')
                    .first()
                )

                cons_residual_obj = (
                    Consequencia.objects
                    .extra(
                        select={'dist': 'ABS(peso - %s)'},
                        select_params=[cons_residual_peso],
                    )
                    .order_by('dist')
                    .first()
                )

                risco.probabilidade_residual = prob_residual_obj or risco.probabilidade_inerente
                risco.consequencia_residual = cons_residual_obj or risco.consequencia_inerente

            risco.save()

            messages.success(
                request,
                f"Plano de tratamento {action_message} com sucesso! "
                f"Risco residual calculado: {float(valor_residual):.2f} "
                f"({nivel_residual.categoria if nivel_residual else 'Não Definido'})."
            )
            return redirect('dashboard')

        except Risco.DoesNotExist:
            messages.error(request, "Risco não encontrado.")
            return redirect('tratamento_riscos')
        except Exception as e:
            messages.error(request, f"Erro ao processar plano de tratamento: {str(e)}")
            return redirect('tratamento_riscos')

    # Shared helpers (mirrors AvaliacaoRiscoView)

    def _get_acceptance_level(self, criterio):
        """Map the organisation's risk appetite to a numeric threshold.

        Mirrors AvaliacaoRiscoView._get_acceptance_level — keep in sync or
        extract to a shared mixin when the project grows.
        """
        if criterio is None:
            return 12

        appetite_thresholds = {
            CriterioAvaliacaoRisco.ApetiteRisco.BAIXO: 8,
            CriterioAvaliacaoRisco.ApetiteRisco.MODERADO: 12,
            CriterioAvaliacaoRisco.ApetiteRisco.ALTO: 16,
        }
        return appetite_thresholds.get(criterio.apetite_risco, 12)


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