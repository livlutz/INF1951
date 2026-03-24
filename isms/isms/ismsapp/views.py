from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.http.response import HttpResponseRedirect
from django.urls.base import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import SignUpForm, LoginForm, UserProfileUpdateForm, UserPasswordChangeForm, CadastroCategoriaAtivoForm, CadastroAtivoForm, CriacaoCriteriosValoracaoAtivosForm
from .models import UserProfile

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

        # Only System Admin and Information Security Auditor can create criteria
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

        # Get all assets for selection
        ativos = Ativo.objects.all()

        # If ativo_id is provided, load that specific asset
        ativo = None
        form = None
        if ativo_id:
            try:
                ativo = Ativo.objects.get(id=ativo_id)
                form = self.form_class(instance=ativo)
            except Ativo.DoesNotExist:
                pass

        if not form:
            form = self.form_class()

        contexto = {
            'form': form,
            'ativos': ativos,
            'ativo_selecionado': ativo,
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
            form.save()
            return redirect('dashboard')

        ativos = Ativo.objects.all()
        contexto = {
            'form': form,
            'ativos': ativos,
            'ativo_selecionado': ativo,
        }
        return render(request, self.template_name, contexto)

class AnaliseValoracaoAtivosView(View):
    """View for analyzing asset valuations (CIDP weights).

    Allows users to view the CIDP ratings for assets and see a calculated
    valuation score based on the ratings.

    Authorized users:
    - System Administrator (SISTEMA_ADMIN)
    - Information Security Auditor (AUDITOR)
    """
    template_name = "ismsapp/analise_valoracao_ativos.html"

    def _check_permission(self, user):
        """Check if user has permission to analyze asset valuations."""
        if not user.is_authenticated:
            return False

        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return False

        # Only System Admin and Information Security Auditor can analyze valuations
        allowed_actors = [
            UserProfile.Actor.ANALISTA,
            UserProfile.Actor.AUDITOR
        ]
        return user_profile.actor_type in allowed_actors

    def _calcular_valor_ativo(self, ativo):
        """Calculate the asset valuation score based on CIDP ratings.

        Returns a dictionary with score and risk level.
        """
        # Calculate average of CIDP ratings
        cidp_values = [
            ativo.confidencialidade,
            ativo.integridade,
            ativo.disponibilidade,
            ativo.privacidade
        ]

        # Filter out zero values (not yet rated)
        rated_values = [v for v in cidp_values if v > 0]

        if not rated_values:
            return {
                'score': 0,
                'score_texto': '0.0',
                'nivel_risco': 'SEM AVALIAÇÃO',
                'classe_risco': 'sem-risco'
            }

        average = sum(rated_values) / len(rated_values)

        # Normalize to scale of 0-5 for display
        score = round(average, 1)

        # Determine risk level based on score
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

        # If ativo_id is provided, load that specific asset
        ativo = None
        valuation_data = None

        if ativo_id:
            try:
                ativo = Ativo.objects.get(id=ativo_id)
                valuation_data = self._calcular_valor_ativo(ativo)
            except Ativo.DoesNotExist:
                pass

        contexto = {
            'ativos': ativos,
            'ativo_selecionado': ativo,
            'valuation_data': valuation_data,
        }
        return render(request, self.template_name, contexto)
