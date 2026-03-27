from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.http.response import HttpResponseRedirect
from django.urls.base import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from .forms import SignUpForm, LoginForm, UserProfileUpdateForm, UserPasswordChangeForm, CadastroCategoriaAtivoForm, CadastroAtivoForm, CriacaoCriteriosValoracaoAtivosForm, CriacaoCriteriosAvaliacaoRiscosForm, IdentificacaoRiscosForm, AnaliseRiscosForm
from .models import UserProfile, CriterioAvaliacaoRisco

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

    @method_decorator(login_required(login_url="login"))
    def post(self, request, *args, **kwargs):
        if not self._check_permission(request.user):
            return redirect('dashboard')

        from .models import Ativo
        import logging
        logger = logging.getLogger(__name__)

        ativo_id = request.POST.get('ativo_id')

        # Log all POST data for debugging
        logger.info(f"📥 POST data received: {dict(request.POST)}")

        if not ativo_id:
            return redirect('dashboard')

        try:
            ativo = Ativo.objects.get(id=ativo_id)
        except Ativo.DoesNotExist:
            return redirect('dashboard')

        # Get CIDP values from POST request
        try:
            confidencialidade = int(request.POST.get('confidencialidade', 0))
            integridade = int(request.POST.get('integridade', 0))
            disponibilidade = int(request.POST.get('disponibilidade', 0))
            privacidade = int(request.POST.get('privacidade', 0))

            logger.info(f"📊 Parsed CIDP values: conf={confidencialidade}, integ={integridade}, disp={disponibilidade}, priv={privacidade}")

            # Validate values are between 0 and 5
            if not all(0 <= val <= 5 for val in [confidencialidade, integridade, disponibilidade, privacidade]):
                raise ValueError("Values must be between 0 and 5")

            # Calculate peso_cidp as the average of non-zero CIDP values
            cidp_values = [confidencialidade, integridade, disponibilidade, privacidade]
            non_zero_values = [v for v in cidp_values if v > 0]

            if non_zero_values:
                peso_cidp = sum(non_zero_values) / len(non_zero_values)
            else:
                peso_cidp = 0

            logger.info(f"🧮 Calculated peso_cidp: {peso_cidp} from values: {non_zero_values}")

            # Update the asset with new CIDP values
            ativo.confidencialidade = confidencialidade
            ativo.integridade = integridade
            ativo.disponibilidade = disponibilidade
            ativo.privacidade = privacidade
            ativo.peso_cidp = peso_cidp

            # Save to database
            ativo.save()
            logger.info(f"✅ Asset {ativo.id} ({ativo.nome}) saved with CIDP values: conf={ativo.confidencialidade}, integ={ativo.integridade}, disp={ativo.disponibilidade}, priv={ativo.privacidade}, peso_cidp={ativo.peso_cidp}")

            # Add success message
            messages.success(request, f'Avaliação do ativo "{ativo.nome}" registrada com sucesso!')

            # Redirect to dashboard with success message
            return redirect('dashboard')
        except (ValueError, TypeError):
            # If there's an error, just redirect back
            return redirect('dashboard')

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
            impactos = form.cleaned_data.get('impactos')

            # Create Risco object with separate fields
            risco = Risco(
                nome=nome,
                descricao=descricao,
                impactos=impactos,
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