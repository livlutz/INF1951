from django.contrib import admin

# Register your models here.
from .models import (
    Ativo, Ameaca, Vulnerabilidade, Consequencia, Probabilidade,
    Nivel, Tratamento, Risco, Controle, CategoriaControle
)


class CategoriaControleAdmin(admin.ModelAdmin):
    """Admin interface for managing control categories.

    Allows viewing the three built-in control categories and their descriptions.
    """
    list_display = ('tipo', 'descricao_preview')
    readonly_fields = ('tipo',)

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('tipo',),
            'description': 'As categorias de controle são pré-definidas pelo sistema.'
        }),
        ('Descrição', {
            'fields': ('descricao',),
            'classes': ('wide',)
        }),
    )

    def descricao_preview(self, obj):
        """Display first 70 characters of description."""
        return obj.descricao[:70] + '...' if len(obj.descricao) > 70 else obj.descricao
    descricao_preview.short_description = 'Descrição'


class ControleAdmin(admin.ModelAdmin):
    """Admin interface for managing security controls.

    Allows administrators to:
    - Create and organize controls by category (preventive, detective, corrective)
    - Define control names and detailed descriptions
    - View which treatments use each control
    - Assign controls to multiple categories
    """
    list_display = ('nome', 'categorias_list', 'descricao_preview')
    list_filter = ('categorias__tipo',)
    search_fields = ('nome', 'descricao')
    filter_horizontal = ('categorias',)
    ordering = ('nome',)

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'categorias')
        }),
        ('Descrição', {
            'fields': ('descricao',),
            'classes': ('wide',)
        }),
    )

    def categorias_list(self, obj):
        """Display categories for this control."""
        cats = obj.categorias.all()
        if cats.exists():
            return ", ".join([cat.get_tipo_display() for cat in cats])
        return "-"
    categorias_list.short_description = 'Categorias'

    def descricao_preview(self, obj):
        """Display first 50 characters of description."""
        return obj.descricao[:50] + '...' if len(obj.descricao) > 50 else obj.descricao
    descricao_preview.short_description = 'Descrição'


class TratamentoAdmin(admin.ModelAdmin):
    """Admin interface for managing treatment plans.

    Allows linking treatment plans to security controls.
    """
    list_display = ('nome', 'tipo_tratamento', 'aceito', 'controles_count')
    list_filter = ('tipo_tratamento', 'aceito')
    search_fields = ('nome', 'descricao')
    filter_horizontal = ('controles',)

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'tipo_tratamento', 'aceito')
        }),
        ('Descrição e Estratégia', {
            'fields': ('descricao',),
            'classes': ('wide',)
        }),
        ('Controles', {
            'fields': ('controles',),
            'classes': ('wide',)
        }),
        ('Efetividade Esperada', {
            'fields': ('reducao_probabilidade', 'reducao_impacto'),
            'description': 'Percentuais de redução esperados com a aplicação deste tratamento'
        }),
    )

    def controles_count(self, obj):
        """Display number of controls associated with this treatment."""
        return obj.controles.count()
    controles_count.short_description = 'Controles'


admin.site.register(Ativo)
admin.site.register(Ameaca)
admin.site.register(Vulnerabilidade)
admin.site.register(Consequencia)
admin.site.register(Probabilidade)
admin.site.register(Nivel)
admin.site.register(CategoriaControle, CategoriaControleAdmin)
admin.site.register(Controle, ControleAdmin)
admin.site.register(Tratamento, TratamentoAdmin)
admin.site.register(Risco)