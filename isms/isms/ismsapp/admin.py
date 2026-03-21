from django.contrib import admin

# Register your models here.
from .models import Ativo, Ameaca, Vulnerabilidade, Consequencia, Probabilidade, Nivel, Tratamento, Risco

admin.site.register(Ativo)
admin.site.register(Ameaca)
admin.site.register(Vulnerabilidade)
admin.site.register(Consequencia)
admin.site.register(Probabilidade)
admin.site.register(Nivel)
admin.site.register(Tratamento)
admin.site.register(Risco)