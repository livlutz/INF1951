from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.http.response import HttpResponseRedirect
from django.urls.base import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import SignUpForm, LoginForm
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
    """Logout view for users to end their session."""

    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(reverse_lazy("home"))


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