# Generated migration for adding risk evaluation decision fields

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("ismsapp", "0008_alter_risco_nome"),
    ]

    operations = [
        migrations.AddField(
            model_name="risco",
            name="decisao_avaliacao",
            field=models.CharField(
                choices=[
                    ("nao_avaliado", "Não Avaliado"),
                    ("aceitar", "Aceitar"),
                    ("tratar", "Enviar para Tratamento"),
                ],
                default="nao_avaliado",
                help_text="Decisão tomada durante a avaliação do risco (UC-08): aceitar, enviar para tratamento, ou não avaliado.",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="risco",
            name="data_avaliacao",
            field=models.DateTimeField(
                blank=True,
                help_text="Data e hora em que o risco foi avaliado.",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="risco",
            name="auditor_avaliacao",
            field=models.ForeignKey(
                blank=True,
                help_text="Auditor responsável pela avaliação do risco.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="riscos_avaliados",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="risco",
            name="observacoes_avaliacao",
            field=models.TextField(
                blank=True,
                default="",
                help_text="Observações, justificativas ou notas adicionais sobre a avaliação.",
            ),
        ),
    ]
