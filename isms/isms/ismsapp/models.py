from django.db import models
from django.contrib.auth.models import User

class Consequencia(models.Model):
    """
    Represents the impact level of a risk event on the organisation.

    Each instance defines a named severity category (e.g. 'Alto', 'Baixo')
    paired with a numeric weight that is used when calculating risk scores.
    The same consequence record can be referenced by a risk twice: once to
    express the impact *before* any controls are applied (inherent), and once
    to express the impact *after* controls are in place (residual).
    """

    class Categoria(models.TextChoices):
        """Ordered severity levels from highest to lowest impact."""

        MUITO_ALTO = "muito_alto","Muito Alto"
        ALTO = "alto","Alto"
        MEDIO = "medio","Médio"
        BAIXO = "baixo","Baixo"
        MUITO_BAIXO = "muito_baixo","Muito Baixo"

    """Numeric weight assigned to this severity level.
    Higher values indicate greater impact and raise the overall risk score."""

    peso = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text=(
            "Peso numérico atribuído a este nível de severidade. "
            "Valores mais altos indicam maior impacto e elevam o valor geral de risco."
        ),
    )

    """Detailed explanation of what this impact level means in practice."""
    descricao = models.TextField(
        help_text = "Explicação detalhada do que este nível de impacto representa na prática.",
    )

    """Named severity category that groups this consequence level."""
    categoria = models.CharField(
        max_length = 20,
        choices = Categoria.choices,
        help_text = "Categoria de severidade que classifica este nível de consequência.",
    )

    class Meta:
        verbose_name = "Consequência"
        verbose_name_plural = "Consequências"

    def __str__(self):
        return f"{self.get_categoria_display()} (peso {self.peso})"

class Probabilidade(models.Model):
    """
    Represents the likelihood that a risk event will actually occur.

    Each instance defines a named frequency or probability category (e.g.
    'Alta' (high), 'Frequente' (frequent)) together with a numeric weight used in risk scoring.
    Like Consequencia (consequence), a Probabilidade (probability) record can be linked to the same risk
    twice — once for the inherent likelihood (ignoring controls) and once for
    the residual likelihood (with controls applied).
    """

    class Categoria(models.TextChoices):
        """Likelihood levels from most to least likely."""
        MUITO_ALTA = "muito_alta", "Muito Alta"
        ALTA = "alta", "Alta"
        MEDIA = "media", "Média"
        BAIXA = "baixa", "Baixa"
        MUITO_BAIXA = "muito_baixa", "Muito Baixa"
        FREQUENTE = "frequente", "Frequente"

    """Numeric weight for this likelihood level. Higher values indicate a greater chance of occurrence and raise the overall risk score."""
    peso = models.DecimalField(
        max_digits = 5,
        decimal_places = 2,
        help_text = (
            "Peso numérico para este nível de probabilidade. "
            "Valores mais altos indicam maior chance de ocorrência e elevam o score geral de risco."
        ),
    )

    """Detailed explanation of what this probability level represents (e.g. frequency range, qualitative orientation)."""
    descricao = models.TextField(
        help_text = "Explicação do que este nível de probabilidade representa (e.g. faixa de frequência, orientação qualitativa).",
    )

    """Named probability category that groups this likelihood level."""
    categoria = models.CharField(
        max_length = 20,
        choices = Categoria.choices,
        help_text = "Categoria de probabilidade que agrupa este nível de probabilidade.",
    )

    class Meta:
        verbose_name = "Probabilidade"
        verbose_name_plural = "Probabilidades"

    def __str__(self):
        return f"{self.get_categoria_display()} (peso {self.peso})"

class Nivel(models.Model):
    """
    Represents the overall risk level that results from combining a consequence
    and a probability score (e.g. 'Crítico', 'Alto', 'Médio', 'Baixo') (critical, high, medium, low).

    Each instance is scoped to either the inherent or the residual risk
    calculation, which allows the same category name to carry a different
    numeric weight depending on the context. When attached to a Risco record,
    the inherent Nivel (level) reflects the exposure before any controls, and the
    residual Nivel (level) reflects the remaining exposure after controls are applied.
    """

    class Tipo(models.TextChoices):
        """Indicates which risk calculation stage this level belongs to."""
        INERENTE = "inerente", "Inerente"
        RESIDUAL = "residual", "Residual"

    """Numeric weight that represents this risk level in the organisation's risk matrix. Higher values indicate more severe risk levels."""
    tipo = models.CharField(
        max_length = 10,
        choices = Tipo.choices,
        help_text = (
            "Define se este nível é utilizado no score de risco inerente "
            "(antes dos controles) ou no score de risco residual (após os controles)."
        ),
    )

    """Numeric weight that represents this risk level in the organisation's risk matrix. Higher values indicate more severe risk levels."""
    peso = models.DecimalField(
        max_digits = 5,
        decimal_places = 2,
        help_text = "Peso numérico que representa este nível de risco dentro da matriz de risco da organização.",
    )

    """Human-readable label for this risk level (e.g. 'Crítico', 'Alto', 'Médio', 'Baixo')."""
    categoria = models.CharField(
        max_length = 100,
        help_text = "Rótulo legível por humanos para este nível de risco (e.g. 'Crítico', 'Alto', 'Médio', 'Baixo').",
    )

    class Meta:
        verbose_name = "Nível"
        verbose_name_plural = "Níveis"

    def __str__(self):
        return f"{self.get_tipo_display()} – {self.categoria} (peso {self.peso})"


class Tratamento(models.Model):
    """
    Describes the strategy chosen to address a specific risk.

    A risk may have more than one treatment (the relationship is many-to-many).
    The treatment type drives how the risk should be handled, while the
    description field captures the concrete actions or decisions taken.

    Treatment strategies:
      - Aceitar (accept)     : The risk is acknowledged and accepted without further action.
      - Mitigar (mitigate)   : Controls are put in place to reduce the likelihood or impact.
      - Evitar (avoid)       : The activity or condition that causes the risk is stopped.
      - Compartilhar (share) : The risk is transferred or shared with a third party (e.g. insurance).
    """

    class TipoTratamento(models.TextChoices):
        ACEITAR = "aceitar", "Aceitar"
        MITIGAR = "mitigar", "Mitigar (Modificar)"
        EVITAR = "evitar", "Evitar"
        COMPARTILHAR = "compartilhar", "Compartilhar"

    """The selected risk treatment strategy for this plan."""
    tipo_tratamento = models.CharField(
        max_length=20,
        choices=TipoTratamento.choices,
        help_text="Estratégia de resposta ao risco selecionada para este tratamento.",
    )

    """Detailed description of the treatment plan, including specific actions, responsible parties, and timelines."""
    descricao = models.TextField(
        help_text=(
            "Detalhes de implementação deste tratamento: quais ações serão tomadas, "
            "quem é o responsável e quaisquer prazos ou decisões relevantes."
        ),
    )

    class Meta:
        verbose_name = "Tratamento"
        verbose_name_plural = "Tratamentos"

    def __str__(self):
        return f"{self.get_tipo_tratamento_display()}"


class Controle(models.Model):
    """
    A specific security or operational control that forms part of a treatment plan.

    Controls are the concrete measures implemented to reduce risk — for example,
    an access policy, a monitoring tool, or a staff training programme. A single
    treatment plan can include multiple controls (one-to-many relationship).

    This model is intentionally minimal. Extend it with a name or reference code
    field when integrating with a control catalogue such as ISO 27001
    """

    """The treatment plan that this control belongs to. Each control is linked to exactly one treatment, but a treatment can have multiple controls."""
    tratamento = models.ForeignKey(
        Tratamento,
        on_delete=models.CASCADE,
        related_name="controles",
        help_text="O plano de tratamento ao qual este controle pertence.",
    )

    """Optional free-text description of the control, which can include a reference code if using a standard control catalogue (e.g. 'A.9.1.1 – Access control policy')."""
    descricao = models.TextField(
        blank=True,
        help_text=(
            "Descrição opcional ou código de referência do controle "
            "(ex.: 'A.9.1.1 – Política de controle de acesso')."
        ),
    )

    class Meta:
        verbose_name = "Controle"
        verbose_name_plural = "Controles"

    def __str__(self):
        return f"Controle #{self.pk} → {self.tratamento}"

class CategoriaAtivo(models.Model):
    """
    Representa uma categoria de ativo utilizada pela organização (UC-01 / RF-01).

    As categorias classificam os ativos em dois grandes grupos:
    primários (aqueles que possuem valor direto para o negócio, como
    informações e serviços) e de suporte (aqueles que sustentam os
    ativos primários, como hardware e software).

    Apenas Administradores do Sistema e Auditores de Segurança da
    Informação podem cadastrar novas categorias.
    """

    class Tipo(models.TextChoices):
        """Classificação do ativo conforme sua relação com o negócio."""
        PRIMARIO = "primario", "Primário"
        SUPORTE  = "suporte",  "De Suporte"

    nome = models.CharField(
        max_length=100,
        unique=True,
        help_text="Nome da categoria. Deve ser único no sistema.",
    )
    tipo = models.CharField(
        max_length=10,
        choices=Tipo.choices,
        help_text=(
            "Tipo do ativo: 'Primário' para ativos com valor direto ao negócio "
            "(ex.: informações, serviços); 'De Suporte' para infraestrutura que "
            "sustenta os ativos primários (ex.: hardware, software, pessoas)."
        ),
    )
    descricao = models.TextField(
        help_text="Descrição detalhada da categoria e dos ativos que ela engloba.",
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        help_text="Data e hora em que a categoria foi registrada no sistema.",
    )

    class Meta:
        verbose_name        = "Categoria de Ativo"
        verbose_name_plural = "Categorias de Ativos"
        ordering            = ["tipo", "nome"]

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"

class Ativo(models.Model):
    """
    An information asset that the organisation needs to protect.

    Assets can be systems, databases, processes, documents, or any other item
    that holds value. Each asset is evaluated across four security dimensions —
    Confidentiality, Integrity, Availability, and Privacy (CIDP) — which are
    scored individually and combined into a single composite weight (peso_cidp)
    used during risk scoring.
    """

    """Name/identifier of the asset (e.g., 'Servidor de Banco de Dados Prod-01')."""
    nome = models.CharField(
        max_length=255,
        default="Ativo",
        help_text="Nome único ou identificador do ativo (ex.: 'Servidor de Banco de Dados Prod-01').",
    )

    """Foreign key to the asset category that classifies this asset."""
    categoria = models.ForeignKey(
        CategoriaAtivo,
        on_delete=models.SET_NULL,
        null=True,
        related_name="ativos",
        help_text="Categoria que classifica este ativo.",
    )

    """Person or department responsible for this asset."""
    responsavel = models.CharField(
        max_length=200,
        default="Responsável",
        help_text="Nome ou departamento responsável por este ativo.",
    )

    """Detailed description of the asset's purpose and characteristics."""
    descricao = models.TextField(
        blank=True,
        help_text="Descrição detalhada da finalidade e características do ativo.",
    )

    """Interdependencies - other assets required for this asset to function."""
    interdependencias = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='dependentes',
        help_text="Ativos necessários para o funcionamento deste ativo.",
    )

    """Numeric score for the Confidentiality dimension, indicating how sensitive the asset's information is. Higher values mean greater damage if data is disclosed without authorization."""
    confidencialidade = models.PositiveSmallIntegerField(
        verbose_name = "Confidencialidade (C)",
        default = 0,
        help_text = (
            "Grau de sensibilidade das informações deste ativo. "
            "Uma pontuação mais alta indica maior prejuízo caso os dados sejam divulgados sem autorização."
        ),
    )

    """Numeric score for the Integrity dimension, indicating how critical it is that the asset's data remains accurate and unaltered. Higher values mean greater harm if data is modified or corrupted."""
    integridade = models.PositiveSmallIntegerField(
        verbose_name = "Integridade (I)",
        default = 0,
        help_text = (
            "Grau de criticalidade do dado deste ativo. "
            "Uma pontuação mais alta indica maior dano se os dados forem modificados ou corrompidos."
        ),
    )

    """Numeric score for the Availability dimension, indicating how important it is that the asset is accessible when needed. Higher values mean more severe impact if the asset becomes unavailable."""
    disponibilidade = models.PositiveSmallIntegerField(
        verbose_name = "Disponibilidade (D)",
        default = 0,
        help_text = (
            "Grau de importância do acesso a este ativo quando necessário. "
            "Uma pontuação mais alta indica impacto mais severo se o ativo se tornar indisponível."
        ),
    )

    """The Privacy dimension score, indicating how much the asset handles personal data subject to privacy regulations. Higher values mean greater exposure to privacy-related obligations and risks."""
    privacidade = models.PositiveSmallIntegerField(
        verbose_name = "Privacidade (P)",
        default = 0,
        help_text = (
            "O grau em que este ativo lida com dados pessoais sujeitos a regulamentações de privacidade. "
            "Uma pontuação mais alta indica maior exposição a obrigações e riscos relacionados à privacidade."
        ),
    )

    """Composite CIDP weight calculated from the four dimension scores previously defined. This value is used in risk scoring to reflect the overall criticality of the asset. Consider overriding the save() method or using a @property to automatically keep this value in sync whenever any of the individual dimension scores are updated."""
    peso_cidp = models.DecimalField(
        max_digits = 5,
        decimal_places = 2,
        default = 0,
        help_text = (
            "Peso composto CIDP calculado a partir das quatro pontuações de dimensão acima. "
        ),
    )

    class Meta:
        verbose_name = "Ativo"
        verbose_name_plural = "Ativos"

    def __str__(self):
        return f"{self.nome}"

class Ameaca(models.Model):
    """
    A threat that could exploit a weakness in a specific asset.

    Threats are always linked to the asset they target. The same threat scenario
    can then be associated with one or more risks and with one or more vulnerabilities that it could exploit.
    """

    """The asset that this threat targets. Each threat is linked to exactly one asset, but an asset can have multiple threats."""
    ativo = models.ForeignKey(
        Ativo,
        on_delete = models.CASCADE,
        related_name = "ameacas",
        help_text = "O ativo que esta ameaça tem como alvo.",
    )

    """Detailed description of the threat scenario, including how it could be triggered and by whom. This should provide enough context to understand the nature of the threat and its potential impact on the asset."""
    descricao = models.TextField(
        help_text = "Descrição detalhada do cenário de ameaça, incluindo como ele poderia ser acionado e por quem.",
    )

    class Meta:
        verbose_name = "Ameaça"
        verbose_name_plural = "Ameaças"

    def __str__(self):
        return f"Ameaça #{self.pk} – {self.ativo}"

class Vulnerabilidade(models.Model):
    """
    A weakness in an asset that a particular threat could exploit.

    A vulnerability only makes sense in the context of a specific asset and a
    specific threat — it answers the question 'how could *this* threat harm
    *this* asset?'. The combination of asset and threat is unique (enforced by
    the database constraint), so each vulnerability record is distinct.

    Example: Asset = 'Portal de clientes', Threat = 'Injeção de SQL',
    Vulnerability = 'Falta de validação de entradas no formulário de login'.
    """

    """The asset that has this vulnerability. Each vulnerability is linked to exactly one asset, but an asset can have multiple vulnerabilities."""
    ativo = models.ForeignKey(
        Ativo,
        on_delete = models.CASCADE,
        related_name = "vulnerabilidades",
        help_text = "O ativo que contém esta vulnerabilidade.",
    )

    """The threat that could exploit this vulnerability. Each vulnerability is linked to exactly one threat, but a threat can be associated with multiple vulnerabilities."""
    ameaca = models.ForeignKey(
        Ameaca,
        on_delete = models.CASCADE,
        related_name = "vulnerabilidades",
        help_text = "A ameaça que poderia explorar esta vulnerabilidade.",
    )

    """Optional free-text description of the specific vulnerability and how it could be exploited. This should provide enough detail to understand the nature of the weakness and its relationship to the associated threat and asset."""
    descricao = models.TextField(
        blank = True,
        help_text = "Descrição opcional da vulnerabilidade específica e como ela poderia ser explorada.",
    )

    class Meta:
        verbose_name = "Vulnerabilidade"
        verbose_name_plural = "Vulnerabilidades"
        unique_together = ("ativo", "ameaca")  # one vulnerability record per asset/threat pair

    def __str__(self):
        return f"Vulnerabilidade #{self.pk} ({self.ativo} / {self.ameaca})"


class Risco(models.Model):
    """
    The central risk record in the application.

    A risk represents the possibility that a threat will exploit a vulnerability
    in an asset and cause harm to the organisation. Each risk is assessed twice:

      - Inherent risk  : the exposure *before* any controls or mitigations are
                         applied. Captured by the _inerente FK triplet
                         (consequencia, probabilidade, nivel) (consequence, probability).
      - Residual risk  : the remaining exposure *after* controls are applied.
                         Captured by the _residual FK triplet.

    Both assessments reference the same Consequencia, Probabilidade, and Nivel
    tables but through separate foreign keys, so the two scores are fully
    independent and can be updated individually as the risk treatment evolves.

    A risk is also linked to one or more treatment plans (Tratamento) through a
    many-to-many relationship, representing the actions the organisation will
    take to bring the residual risk to an acceptable level.
    """

    class Tipo(models.TextChoices):
        """
        Indicates whether this record represents the inherent or residual
        risk assessment. In practice most workflows create a single Risco
        record per scenario and populate both _inerente and _residual fields
        on that same record, but the field allows explicit labelling when needed.
        """
        INERENTE = "inerente", "Inerente"
        RESIDUAL = "residual", "Residual"

    #Origin

    """The asset that is exposed to this risk. Each risk is linked to exactly one asset, but an asset can have multiple risks."""
    ativo = models.ForeignKey(
        Ativo,
        on_delete = models.CASCADE,
        related_name = "riscos",
        help_text = "O ativo que é exposto a este risco.",
    )

    """One or more threats that contribute to this risk scenario. A risk can be associated with multiple threats, and a single threat can be linked to multiple risks."""
    ameacas = models.ManyToManyField(
        Ameaca,
        related_name = "riscos",
        blank = True,
        help_text = "As ameaças que contribuem para este cenário de risco.",
    )

    #Classification

    """The name or title of the risk."""
    nome = models.CharField(
        max_length = 255,
        blank = False,
        help_text = "Nome ou título do risco.",
    )

    """Indicates whether this record is an inherent or residual risk assessment. This field is mainly for labelling and filtering purposes, as the actual scores are determined by the respective FK fields. In practice, most scenarios will have both an inherent and a residual assessment within the same Risco record, but this field allows explicit categorization when needed."""
    tipo = models.CharField(
        max_length = 10,
        choices = Tipo.choices,
        help_text = "Indica se este registro está rotulado como uma avaliação de risco inerente ou residual.",
    )

    """Detailed description of the risk scenario, including how the associated threats could exploit vulnerabilities in the asset and what the potential consequences would be. This should provide enough context to understand the nature of the risk and inform the assessment and treatment process."""
    descricao = models.TextField(
        help_text = "Descrição completa do cenário de risco: o que poderia acontecer, por quê, e qual seria o impacto.",
    )

    """Documented potential losses and impacts if this risk materializes (financial, operational, reputational, etc.)."""
    impactos = models.TextField(
        blank = True,
        default = "",
        help_text = "Perdas potenciais e impactos se o risco se materializar (financeiros, operacionais, reputacionais, etc.).",
    )

    #Inherent risk scores (before controls)

    """The severity of the impact if this risk materialises and no controls are in place. This FK references a Consequencia record that defines the inherent consequence level for this risk scenario."""
    consequencia_inerente = models.ForeignKey(
        Consequencia,
        on_delete = models.PROTECT,
        related_name = "riscos_inerentes",
        null = True,
        blank = True,
        help_text = "A severidade do impacto se este risco materializar e não houver controles em vigor.",
    )

    """The likelihood that this risk will occur if no controls are in place. This FK references a Probabilidade record that defines the inherent probability level for this risk scenario."""
    probabilidade_inerente = models.ForeignKey(
        Probabilidade,
        on_delete = models.PROTECT,
        related_name = "riscos_inerentes",
        null = True,
        blank = True,
        help_text = "A probabilidade de este risco ocorrer sem qualquer controle em vigor.",
    )

    """The overall inherent risk level derived from combining the inherent consequence and probability scores. This FK references a Nivel record that defines the inherent risk level for this scenario. The Nivel records linked here should be of the 'Inerente' type to reflect that they are part of the inherent risk assessment."""
    nivel_inerente = models.ForeignKey(
        Nivel,
        on_delete = models.PROTECT,
        related_name = "riscos_inerentes",
        limit_choices_to = {"tipo": Nivel.Tipo.INERENTE},
        null = True,
        blank = True,
        help_text = (
            "O nível geral de risco inerente derivado da combinação da consequência "
            "e da probabilidade inerentes (ex.: 'Crítico', 'Alto')."
        ),
    )

    """The numerical value of the inherent risk, calculated as probability × consequence."""
    valor_risco_inerente = models.DecimalField(
        max_digits = 5,
        decimal_places = 2,
        null = True,
        blank = True,
        help_text = "Valor numérico do risco inerente (probabilidade × consequência).",
    )

    #Residual risk scores (after controls)

    """The severity of the impact after the planned controls or mitigations have been applied. This FK references a Consequencia record that defines the residual consequence level for this risk scenario."""
    consequencia_residual = models.ForeignKey(
        Consequencia,
        on_delete = models.PROTECT,
        related_name = "riscos_residuais",
        null = True,
        blank = True,
        help_text = "A severidade do impacto após a aplicação dos controles ou mitigações planejados.",
    )

    """The likelihood that this risk will still occur after the planned controls or mitigations have been applied. This FK references a Probabilidade record that defines the residual probability level for this risk scenario."""
    probabilidade_residual = models.ForeignKey(
        Probabilidade,
        on_delete = models.PROTECT,
        related_name = "riscos_residuais",
        null = True,
        blank = True,
        help_text = "A probabilidade de este risco ainda ocorrer após a aplicação dos controles.",
    )

    """The overall residual risk level derived from combining the residual consequence and probability scores. This FK references a Nivel record that defines the residual risk level for this scenario. The Nivel records linked here should be of the 'Residual' type to reflect that they are part of the residual risk assessment. This is the target level the organisation aims to reach through treatment."""
    nivel_residual = models.ForeignKey(
        Nivel,
        on_delete = models.PROTECT,
        related_name = "riscos_residuais",
        limit_choices_to = {"tipo": Nivel.Tipo.RESIDUAL},
        null = True,
        blank = True,
        help_text = (
            "O nível geral de risco residual derivado da combinação da consequência "
            "e da probabilidade residuais. Este é o nível alvo que a organização "
            "pretende alcançar por meio do tratamento."
        ),
    )

    """The numerical value of the residual risk, calculated as probability × consequence after controls."""
    valor_risco_residual = models.DecimalField(
        max_digits = 5,
        decimal_places = 2,
        null = True,
        blank = True,
        help_text = "Valor numérico do risco residual após aplicação dos controles.",
    )

    #Treatment

    """The treatment plans selected to address this risk. More than one treatment can apply (e.g. mitigar + compartilhar), and a single treatment plan can be linked to multiple risks if it addresses common scenarios."""
    tratamentos = models.ManyToManyField(
        Tratamento,
        related_name = "riscos",
        blank = True,
        help_text = (
            "Os planos de tratamento selecionados para lidar com este risco. "
            "Mais de um tratamento pode ser aplicado (e.g. mitigar + compartilhar)."
        ),
    )

    class Meta:
        verbose_name = "Risco"
        verbose_name_plural = "Riscos"

    def __str__(self):
        return f"Risco #{self.pk} – {self.nome} ({self.ativo})"


class CriterioAvaliacaoRisco(models.Model):
    """
    Stores the risk evaluation criteria set for the organization.

    This model defines the scales for probability, consequence, and risk appetite
    that are used to evaluate and classify organizational risks.
    There should typically be only one active instance of this model.
    """

    class ApetiteRisco(models.TextChoices):
        """Organizational risk appetite levels."""
        BAIXO = "baixo", "Baixo"
        MODERADO = "moderado", "Moderado"
        ALTO = "alto", "Alto"

    # Probability scale: 1-5 from MUITO_BAIXO to MUITO_ALTO
    escala_probabilidade_1 = models.CharField(
        max_length=100,
        default="Muito Baixo",
        help_text="Descrição do nível 1 de probabilidade"
    )
    escala_probabilidade_2 = models.CharField(
        max_length=100,
        default="Baixo",
        help_text="Descrição do nível 2 de probabilidade"
    )
    escala_probabilidade_3 = models.CharField(
        max_length=100,
        default="Médio",
        help_text="Descrição do nível 3 de probabilidade"
    )
    escala_probabilidade_4 = models.CharField(
        max_length=100,
        default="Alto",
        help_text="Descrição do nível 4 de probabilidade"
    )
    escala_probabilidade_5 = models.CharField(
        max_length=100,
        default="Muito Alto",
        help_text="Descrição do nível 5 de probabilidade"
    )

    # Consequence scale: 1-5 from MUITO_BAIXO to MUITO_ALTO
    escala_consequencia_1 = models.CharField(
        max_length=100,
        default="Muito Baixo",
        help_text="Descrição do nível 1 de consequência"
    )
    escala_consequencia_2 = models.CharField(
        max_length=100,
        default="Baixo",
        help_text="Descrição do nível 2 de consequência"
    )
    escala_consequencia_3 = models.CharField(
        max_length=100,
        default="Médio",
        help_text="Descrição do nível 3 de consequência"
    )
    escala_consequencia_4 = models.CharField(
        max_length=100,
        default="Alto",
        help_text="Descrição do nível 4 de consequência"
    )
    escala_consequencia_5 = models.CharField(
        max_length=100,
        default="Muito Alto",
        help_text="Descrição do nível 5 de consequência"
    )

    # Organizational risk appetite
    apetite_risco = models.CharField(
        max_length=20,
        choices=ApetiteRisco.choices,
        default=ApetiteRisco.MODERADO,
        help_text="Nível de apetite ao risco organizacional"
    )


    class Meta:
        verbose_name = "Critério de Avaliação de Risco"
        verbose_name_plural = "Critérios de Avaliação de Risco"

    def __str__(self):
        return f"Critério de Avaliação de Risco - Apetite: {self.get_apetite_risco_display()}"

#user classes

class UserProfile(models.Model):
    """
    Extended user profile to support role-based access control.
    Associates each Django user with one of the 3 system actors.
    """

    class Actor(models.TextChoices):
        SISTEMA_ADMIN = "admin", "Administrador do sistema"
        AUDITOR = "auditor", "Auditor de Segurança da Informação"
        ANALISTA = "analista", "Analista de Segurança"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    actor_type = models.CharField(
        max_length=20,
        choices=Actor.choices,
        help_text="Tipo de usuario que define as permissões e funcionalidades disponíveis",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuários"

    def __str__(self):
        return f"{self.user.username} - {self.get_actor_type_display()}"

    @property
    def is_administrador(self):
        return self.actor_type == self.Actor.SISTEMA_ADMIN
