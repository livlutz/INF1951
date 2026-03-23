from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.http.response import HttpResponseRedirect
from django.urls.base import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import SignUpForm, LoginForm, UserProfileUpdateForm, UserPasswordChangeForm
from .models import UserProfile

class HomeView(View):
    """Home page view - displays landing page."""
    template_name = "ismsapp/home.html"

    def get(self, request, *args, **kwargs):
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
    """
    template_name = "ismsapp/dashboard.html"

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
    Requer que o usuário esteja autenticado.
    """
    template_name = "ismsapp/cadastro_categoria_ativo.html"

