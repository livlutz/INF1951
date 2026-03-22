# forms.py
from django import forms
from django.contrib.auth.models import User
from .models import UserProfile


class SignUpForm(forms.Form):
    """Sign up form for new users to create an account.

    This form includes fields for username, email, password, and actor type (role).
    The save method creates a new User and UserProfile based on the provided data.
    """
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Nome de usuário"
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Email"
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Senha"
        })
    )

    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirmar Senha"
        }),
        label="Confirmar Senha"
    )

    actor_type = forms.ChoiceField(
        choices=UserProfile.Actor.choices,
        label="Tipo de Usuário",
        help_text="Selecione o papel que este usuário terá no sistema.",
        widget=forms.Select(attrs={
            "class": "form-control"
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("As senhas não correspondem.")

        return cleaned_data

    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
        )

        UserProfile.objects.create(
            user=user,
            actor_type=self.cleaned_data["actor_type"],
        )

        return user


class LoginForm(forms.Form):
    """Login form for existing users.

    This form includes fields for email and password.
    """
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Email"
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Senha"
        })
    )


class UserProfileUpdateForm(forms.Form):
    """Form for users to update their profile information.

    This form allows users to update their email address.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Email"
        })
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_email(self):
        email = self.cleaned_data.get("email")

        # Check if email is already taken by another user
        if email != self.user.email:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("Este email já está registrado.")

        return email

    def save(self):
        """Update the user's email address."""
        self.user.email = self.cleaned_data["email"]
        self.user.save()
        return self.user