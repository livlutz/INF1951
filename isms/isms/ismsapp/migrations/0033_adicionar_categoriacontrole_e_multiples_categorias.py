# Generated migration for adding CategoriaControle model and multi-category support

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ismsapp', '0032_reestruturar_controle_categorias'),
    ]

    operations = [
        # Create the new CategoriaControle model
        migrations.CreateModel(
            name='CategoriaControle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(
                    choices=[
                        ('preventivo', 'Preventivo'),
                        ('detectivo', 'Detectivo'),
                        ('corretivo', 'Corretivo/Contingência')
                    ],
                    help_text='Tipo de categoria de controle.',
                    max_length=20,
                    unique=True
                )),
                ('descricao', models.TextField(
                    default='',
                    help_text='Descrição do tipo de controle.'
                )),
            ],
            options={
                'verbose_name': 'Categoria de Controle',
                'verbose_name_plural': 'Categorias de Controle',
            },
        ),
        # Add categorias ManyToMany field to Controle
        migrations.AddField(
            model_name='controle',
            name='categorias',
            field=models.ManyToManyField(
                help_text='Categorias às quais este controle pertence (Preventivo, Detectivo, ou Corretivo/Contingência).',
                related_name='controles',
                to='ismsapp.categoriacontrole'
            ),
        ),
        # Remove old categoria CharField from Controle
        migrations.RemoveField(
            model_name='controle',
            name='categoria',
        ),
        # Update model options for Controle
        migrations.AlterModelOptions(
            name='controle',
            options={'ordering': ['nome'], 'verbose_name': 'Controle', 'verbose_name_plural': 'Controles'},
        ),
    ]
