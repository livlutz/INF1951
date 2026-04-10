# Generated migration for adding aceito field to Tratamento

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ismsapp', '0029_tratamento_nome_remove_tratamento_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='tratamento',
            name='aceito',
            field=models.BooleanField(
                default=False,
                help_text='Marca se este tratamento é uma decisão de aceitação do risco (sem ações adicionais).',
            ),
        ),
    ]
