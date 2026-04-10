# Generated migration for adding nome to Tratamento and removing responsavel and prazo

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ismsapp', '0028_remove_risco_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='tratamento',
            name='nome',
            field=models.CharField(
                default='Sem nome',
                help_text='Nome do plano de tratamento.',
                max_length=255,
            ),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='tratamento',
            name='responsavel',
        ),
        migrations.RemoveField(
            model_name='tratamento',
            name='prazo',
        ),
    ]
