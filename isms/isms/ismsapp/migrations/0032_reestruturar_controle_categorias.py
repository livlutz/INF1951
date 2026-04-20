# Generated migration for restructuring Controle model with categories

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ismsapp', '0031_remove_controle_descricao'),
    ]

    operations = [
        # Add new fields to Controle
        migrations.AddField(
            model_name='controle',
            name='categoria',
            field=models.CharField(
                choices=[('preventivo', 'Preventivo'), ('detectivo', 'Detectivo'), ('corretivo', 'Corretivo/Contingência')],
                default='preventivo',
                help_text='Categoria do controle: Preventivo, Detectivo, ou Corretivo/Contingência.',
                max_length=20
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='controle',
            name='descricao',
            field=models.TextField(default='', help_text='Descrição detalhada do controle: seu propósito, escopo e como deve ser implementado.'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='controle',
            name='nome',
            field=models.CharField(default='Controle', help_text="Nome ou título do controle (ex: 'Autenticação Multi-Fator', 'Monitoramento de Logs').", max_length=255),
            preserve_default=False,
        ),
        # Remove the old ForeignKey to Tratamento
        migrations.RemoveField(
            model_name='controle',
            name='tratamento',
        ),
        # Add ManyToMany relationship between Tratamento and Controle
        migrations.AddField(
            model_name='tratamento',
            name='controles',
            field=models.ManyToManyField(
                blank=True,
                help_text='Controles que fazem parte deste plano de tratamento.',
                related_name='tratamentos',
                to='ismsapp.controle'
            ),
        ),
        # Add ordering to Controle
        migrations.AlterModelOptions(
            name='controle',
            options={'ordering': ['categoria', 'nome'], 'verbose_name': 'Controle', 'verbose_name_plural': 'Controles'},
        ),
    ]
