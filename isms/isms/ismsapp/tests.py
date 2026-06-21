from django.test import TestCase

from .models import CategoriaControle, Controle
from .views import TratamentoRiscoView


class TratamentoRiscoControlReductionTests(TestCase):
	@classmethod
	def setUpTestData(cls):
		cls.categoria_preventiva, _ = CategoriaControle.objects.get_or_create(
			tipo=CategoriaControle.Tipo.PREVENTIVO,
			defaults={'descricao': 'Categoria preventiva de teste'},
		)
		cls.categoria_detectiva, _ = CategoriaControle.objects.get_or_create(
			tipo=CategoriaControle.Tipo.DETECTIVO,
			defaults={'descricao': 'Categoria detectiva de teste'},
		)
		cls.categoria_corretiva, _ = CategoriaControle.objects.get_or_create(
			tipo=CategoriaControle.Tipo.CORRETIVO,
			defaults={'descricao': 'Categoria corretiva de teste'},
		)

		cls.controle_preventivo = Controle.objects.create(
			nome='Controle Preventivo',
			descricao='Controle preventivo de teste',
		)
		cls.controle_preventivo.categorias.add(cls.categoria_preventiva)

		cls.controle_detectivo = Controle.objects.create(
			nome='Controle Detectivo',
			descricao='Controle detectivo de teste',
		)
		cls.controle_detectivo.categorias.add(cls.categoria_detectiva)

		cls.controle_corretivo = Controle.objects.create(
			nome='Controle Corretivo',
			descricao='Controle corretivo de teste',
		)
		cls.controle_corretivo.categorias.add(cls.categoria_corretiva)

	def test_reduction_is_cumulative_by_selected_control(self):
		controles = Controle.objects.filter(
			id__in=[
				self.controle_preventivo.id,
				self.controle_detectivo.id,
				self.controle_corretivo.id,
			]
		).prefetch_related('categorias')

		results = TratamentoRiscoView()._calculate_control_reductions(controles)

		self.assertEqual(results['prob_reduction'], 20.0)
		self.assertEqual(results['impact_reduction'], 20.0)
		self.assertTrue(results['has_controls'])

	def test_detective_control_counts_for_both_axes(self):
		controles = Controle.objects.filter(id=self.controle_detectivo.id).prefetch_related('categorias')

		results = TratamentoRiscoView()._calculate_control_reductions(controles)

		self.assertEqual(results['prob_reduction'], 10.0)
		self.assertEqual(results['impact_reduction'], 10.0)
