# Generated migration for removing descricao field from Controle

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ismsapp', '0030_tratamento_aceito'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='controle',
            name='descricao',
        ),
    ]
