# Generated migration for removing risco fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ismsapp', '0027_alter_vulnerabilidade_nome'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='risco',
            name='ameacas',
        ),
        migrations.RemoveField(
            model_name='risco',
            name='impactos',
        ),
        migrations.RemoveField(
            model_name='risco',
            name='decisao_avaliacao',
        ),
        migrations.RemoveField(
            model_name='risco',
            name='observacoes_avaliacao',
        ),
    ]
