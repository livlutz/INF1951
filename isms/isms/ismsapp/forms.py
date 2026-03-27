# forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Ativo, Risco, UserProfile, CategoriaAtivo, CriterioAvaliacaoRisco


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


class UserPasswordChangeForm(forms.Form):
    """Form for users to change their password.

    This form includes fields for current password and new password confirmation.
    Validates that the current password is correct and new passwords match.
    """
    old_password = forms.CharField(
        label="Senha Atual",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Senha Atual"
        })
    )

    new_password1 = forms.CharField(
        label="Nova Senha",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Nova Senha"
        })
    )

    new_password2 = forms.CharField(
        label="Confirmar Nova Senha",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirmar Nova Senha"
        })
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_old_password(self):
        """Validate that the old password is correct."""
        old_password = self.cleaned_data.get("old_password")

        if not self.user.check_password(old_password):
            raise forms.ValidationError("Senha atual incorreta.")

        return old_password

    def clean(self):
        """Validate that new passwords match."""
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")

        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("As novas senhas não correspondem.")

        return cleaned_data

    def save(self):
        """Update the user's password."""
        self.user.set_password(self.cleaned_data["new_password1"])
        self.user.save()
        return self.user

class CadastroCategoriaAtivoForm(forms.ModelForm):
    """Form for registering asset categories.

    This form allows authorized users (System Administrators and Information Security Auditors)
    to register new asset categories in the system.
    """

    class Meta:
        model = CategoriaAtivo
        fields = ['nome', 'tipo', 'descricao']
        labels = {
            'nome': 'Nome da Categoria',
            'tipo': 'Tipo de Categoria',
            'descricao': 'Descrição'
        }
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Sistemas de Faturamento',
                'maxlength': '100'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-control',
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descreva brevemente o propósito desta categoria...',
                'rows': 6
            })
        }


class CadastroAtivoForm(forms.ModelForm):
    """Form for registering assets.

    This form allows authorized users to register new assets in the system
    with their basic information (name, category, responsible person, description,
    and interdependencies).
    """

    class Meta:
        from .models import Ativo
        model = Ativo
        fields = ['nome', 'categoria', 'responsavel', 'descricao', 'interdependencias']
        labels = {
            'nome': 'Nome do Ativo',
            'categoria': 'Categoria',
            'responsavel': 'Responsável',
            'descricao': 'Descrição',
            'interdependencias': 'Interdependências'
        }
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Servidor de Banco de Dados Prod-01',
                'maxlength': '255'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-control',
            }),
            'responsavel': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome ou Departamento',
                'maxlength': '200'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descreva brevemente a finalidade e as características do ativo...',
                'rows': 5
            }),
            'interdependencias': forms.SelectMultiple(attrs={
                'class': 'form-control interdependencias-select',
            })
        }


class CriacaoCriteriosValoracaoAtivosForm(forms.ModelForm):
    """Form for creating/setting valuation criteria (CIDP weights) for assets.

    This form allows authorized users to define the importance/weight of each
    CIDP dimension (Confidentiality, Integrity, Availability, Privacy) for a
    specific asset on a scale of 1-5.
    """

    class Meta:
        from .models import Ativo
        model = Ativo
        fields = ['confidencialidade', 'integridade', 'disponibilidade', 'privacidade']
        labels = {
            'confidencialidade': 'Confidencialidade',
            'integridade': 'Integridade',
            'disponibilidade': 'Disponibilidade',
            'privacidade': 'Privacidade'
        }
        widgets = {
            'confidencialidade': forms.NumberInput(attrs={
                'class': 'form-control cidp-rating',
                'type': 'number',
                'min': '1',
                'max': '5',
                'value': '1'
            }),
            'integridade': forms.NumberInput(attrs={
                'class': 'form-control cidp-rating',
                'type': 'number',
                'min': '1',
                'max': '5',
                'value': '1'
            }),
            'disponibilidade': forms.NumberInput(attrs={
                'class': 'form-control cidp-rating',
                'type': 'number',
                'min': '1',
                'max': '5',
                'value': '1'
            }),
            'privacidade': forms.NumberInput(attrs={
                'class': 'form-control cidp-rating',
                'type': 'number',
                'min': '1',
                'max': '5',
                'value': '1'
            })
        }


class CriacaoCriteriosAvaliacaoRiscosForm(forms.ModelForm):
    """Form for creating risk evaluation criteria.

    This form allows authorized users (System Administrators and Information Security Auditors)
    to define the probability scales, consequence scales, and organizational risk appetite.
    """

    class Meta:
        model = CriterioAvaliacaoRisco
        fields = [
            'escala_probabilidade_1', 'escala_probabilidade_2', 'escala_probabilidade_3',
            'escala_probabilidade_4', 'escala_probabilidade_5',
            'escala_consequencia_1', 'escala_consequencia_2', 'escala_consequencia_3',
            'escala_consequencia_4', 'escala_consequencia_5',
            'apetite_risco'
        ]
        labels = {
            'escala_probabilidade_1': 'Nível 1 (Muito Baixo)',
            'escala_probabilidade_2': 'Nível 2 (Baixo)',
            'escala_probabilidade_3': 'Nível 3 (Médio)',
            'escala_probabilidade_4': 'Nível 4 (Alto)',
            'escala_probabilidade_5': 'Nível 5 (Muito Alto)',
            'escala_consequencia_1': 'Nível 1 (Muito Baixo)',
            'escala_consequencia_2': 'Nível 2 (Baixo)',
            'escala_consequencia_3': 'Nível 3 (Médio)',
            'escala_consequencia_4': 'Nível 4 (Alto)',
            'escala_consequencia_5': 'Nível 5 (Muito Alto)',
            'apetite_risco': 'Apetite ao Risco Organizacional'
        }
        widgets = {
            'escala_probabilidade_1': forms.TextInput(attrs={
                'class': 'form-control scale-input',
                'placeholder': 'Ex: Muito improvável'
            }),
            'escala_probabilidade_2': forms.TextInput(attrs={
                'class': 'form-control scale-input',
                'placeholder': 'Ex: Improvável'
            }),
            'escala_probabilidade_3': forms.TextInput(attrs={
                'class': 'form-control scale-input',
                'placeholder': 'Ex: Possível'
            }),
            'escala_probabilidade_4': forms.TextInput(attrs={
                'class': 'form-control scale-input',
                'placeholder': 'Ex: Provável'
            }),
            'escala_probabilidade_5': forms.TextInput(attrs={
                'class': 'form-control scale-input',
                'placeholder': 'Ex: Muito provável'
            }),
            'escala_consequencia_1': forms.TextInput(attrs={
                'class': 'form-control scale-input',
                'placeholder': 'Ex: Sem impacto'
            }),
            'escala_consequencia_2': forms.TextInput(attrs={
                'class': 'form-control scale-input',
                'placeholder': 'Ex: Impacto menor'
            }),
            'escala_consequencia_3': forms.TextInput(attrs={
                'class': 'form-control scale-input',
                'placeholder': 'Ex: Impacto moderado'
            }),
            'escala_consequencia_4': forms.TextInput(attrs={
                'class': 'form-control scale-input',
                'placeholder': 'Ex: Impacto significativo'
            }),
            'escala_consequencia_5': forms.TextInput(attrs={
                'class': 'form-control scale-input',
                'placeholder': 'Ex: Impacto crítico'
            }),
            'apetite_risco': forms.Select(attrs={
                'class': 'form-control'
            })
        }

class IdentificacaoRiscosForm(forms.Form):
    """Form for identifying risks related to assets.

    This form allows users to identify and describe risks associated with specific assets,
    including the risk name, description, associated asset, and possible impacts.
    """

    nome = forms.CharField(
        max_length=255,
        label='Nome do Risco',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome do Risco'
        })
    )

    descricao = forms.CharField(
        label='Descrição do Risco',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Descreva o risco em detalhes...',
            'rows': 5
        })
    )

    ativo = forms.ModelChoiceField(
        label='Ativo Associado',
        queryset=Ativo.objects.all(),
        empty_label='Selecione o ativo correspondente',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    impactos = forms.CharField(
        label='Possíveis Impactos',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Documente as perdas potenciais (financeiras, operacionais, reputacionais)...',
            'rows': 5
        })
    )

class AnaliseRiscosForm(forms.Form):
    """Form for analyzing identified risks.

    This form allows users to evaluate the probability and consequence of identified risks
    based on the organization's defined criteria, and to provide a justification for the
    assigned ratings.
    """

    risco = forms.ModelChoiceField(
        label='Risco a Analisar',
        queryset=Risco.objects.filter(tipo=Risco.Tipo.INERENTE),
        empty_label='Selecione o risco a ser analisado',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    probabilidade = forms.ChoiceField(
        label='Probabilidade',
        choices=[(i, f'Nível {i}') for i in range(1, 6)],
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    consequencia = forms.ChoiceField(
        label='Consequência',
        choices=[(i, f'Nível {i}') for i in range(1, 6)],
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    justificativa = forms.CharField(
        label='Justificativa para as Avaliações',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Explique os motivos por trás das avaliações de probabilidade e consequência...',
            'rows': 5
        })
    )