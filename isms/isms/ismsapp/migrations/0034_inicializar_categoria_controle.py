# Migration to initialize CategoriaControle with the three standard types

from django.db import migrations


def create_control_categories(apps, schema_editor):
    """Create the three standard control categories."""
    CategoriaControle = apps.get_model('ismsapp', 'CategoriaControle')

    categories = [
        {
            'tipo': 'preventivo',
            'descricao': 'Controles Preventivos: Ações que evitam ou reduzem a probabilidade de ocorrência de um evento de risco. Implementados antes da ameaça materializar-se.'
        },
        {
            'tipo': 'detectivo',
            'descricao': 'Controles Detectivos: Ações que identificam, descobrem ou reconhecem um evento de risco quando ele ocorre ou tenta ocorrer. Focados em detecção e notificação.'
        },
        {
            'tipo': 'corretivo',
            'descricao': 'Controles Corretivos/Contingência: Ações que remediame reduzem o impacto de um evento de risco após sua ocorrência. Incluem respostas a incidentes e recuperação.'
        }
    ]

    for cat_data in categories:
        CategoriaControle.objects.get_or_create(
            tipo=cat_data['tipo'],
            defaults={'descricao': cat_data['descricao']}
        )


def remove_control_categories(apps, schema_editor):
    """Remove the control categories (reverse operation)."""
    CategoriaControle = apps.get_model('ismsapp', 'CategoriaControle')
    CategoriaControle.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('ismsapp', '0033_adicionar_categoriacontrole_e_multiples_categorias'),
    ]

    operations = [
        migrations.RunPython(create_control_categories, remove_control_categories),
    ]
