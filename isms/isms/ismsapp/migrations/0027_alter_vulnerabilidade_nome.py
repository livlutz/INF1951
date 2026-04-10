# Generated migration for removing default from vulnerabilidade nome field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ismsapp', '0026_remove_vulnerabilidade_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vulnerabilidade',
            name='nome',
            field=models.CharField(
                max_length=255,
                help_text='Nome ou título da vulnerabilidade identificada (ex: Falta de validação de entradas).',
            ),
        ),
    ]
