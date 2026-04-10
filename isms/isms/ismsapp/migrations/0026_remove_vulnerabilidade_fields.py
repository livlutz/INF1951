# Generated migration for removing vulnerabilidade fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ismsapp', '0025_remove_ameaca_default_nome'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vulnerabilidade',
            name='descricao',
        ),
        migrations.RemoveField(
            model_name='vulnerabilidade',
            name='nivel_severidade',
        ),
        migrations.RemoveField(
            model_name='vulnerabilidade',
            name='prioridade_correcao',
        ),
        migrations.RemoveField(
            model_name='vulnerabilidade',
            name='status',
        ),
    ]
