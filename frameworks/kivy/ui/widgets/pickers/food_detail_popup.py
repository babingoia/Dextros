from logging import getLogger

from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout

from infrastructure.path_provider_service import get_asset_path

Builder.load_file(get_asset_path('frameworks/kivy/ui/widgets/pickers/food_detail_popup.kv'))

logger = getLogger(__name__)


def format_nutrient_value(value) -> str:
    """Formata um valor por 100g para exibição brasileira (vírgula decimal).
    None vira "—" — dado indisponível na tabela é diferente de zero."""
    if value is None:
        return "—"
    return f"{value:.1f}".replace(".", ",")


def _format_scaled(value, grams) -> str:
    """Escala um valor por 100g para a porção informada (regra de três de
    apresentação — o cálculo de registro continua no CalculateNutritionUseCase)."""
    if value is None:
        return "—"
    return format_nutrient_value(value * grams / 100)


class FoodDetailContent(BoxLayout):
    """Detalhes de um alimento da TACO (valores por 100g), campo de quantidade
    com recálculo ao vivo e botão Adicionar. A fonte de dados é o Food injetado —
    o widget não conhece router nem use case. O evento on_use_food(food, grams)
    é o mesmo contrato que o popup de busca usava com o rodapé de quantidade."""

    __events__ = ("on_use_food",)

    food = ObjectProperty(None)
    message = StringProperty("")

    energy_text = StringProperty("—")
    protein_text = StringProperty("—")
    carb_text = StringProperty("—")
    fat_text = StringProperty("—")
    fiber_text = StringProperty("—")
    sodium_text = StringProperty("—")
    portion_summary = StringProperty("")

    def __init__(self, food=None, **kwargs):
        super().__init__(**kwargs)
        # Seta a property explicitamente (não via kwarg do super().__init__):
        # o on_food dispara com a mudança None -> Food e aplica os textos.
        self.food = food

    def on_food(self, instance, value):
        """Único ponto de entrada do alimento no widget: __init__ e qualquer
        re-set da property caem aqui, que atualiza os textos e o preview."""
        self._apply_food(value)

    def _apply_food(self, food):
        if food is None:
            self.energy_text = self.protein_text = self.carb_text = "—"
            self.fat_text = self.fiber_text = self.sodium_text = "—"
            self.portion_summary = ""
            return
        self.energy_text = format_nutrient_value(food.energy_kcal)
        self.protein_text = format_nutrient_value(food.protein_g)
        self.carb_text = format_nutrient_value(food.carbohydrate_g)
        self.fat_text = format_nutrient_value(food.fat_g)
        self.fiber_text = format_nutrient_value(food.fiber_g)
        self.sodium_text = format_nutrient_value(food.sodium_mg)
        self._update_portion()

    def _parse_grams(self):
        """Lê e valida a quantidade digitada. Retorna float ou None (com a
        mensagem de erro em self.message quando inválida)."""
        raw = self.ids.grams_input.text.strip().replace(",", ".")
        if not raw:
            return None
        try:
            grams = float(raw)
        except ValueError:
            return None
        if grams < 0:
            return None
        return grams

    def _update_portion(self, *args):
        """Recalcula os valores da porção enquanto o usuário digita. Erro de
        digitação não é erro de registro — o preview só some."""
        grams = self._parse_grams()
        if grams is None or self.food is None:
            self.portion_summary = ""
            return
        grams_display = f"{grams:g}".replace(".", ",")
        self.portion_summary = (
            f"{grams_display} g ≈ "
            f"CHO {_format_scaled(self.food.carbohydrate_g, grams)} g · "
            f"Gordura {_format_scaled(self.food.fat_g, grams)} g · "
            f"{_format_scaled(self.food.energy_kcal, grams)} kcal"
        )

    def confirm(self):
        if self.food is None:
            self.message = "Nenhum alimento selecionado"
            return

        grams_raw = self.ids.grams_input.text.strip().replace(",", ".")
        if not grams_raw:
            self.message = "Informe a quantidade consumida em gramas"
            return

        try:
            grams = float(grams_raw)
        except ValueError:
            self.message = "Quantidade inválida — informe um número (ex.: 150)"
            return

        if grams < 0:
            self.message = "Quantidade negativa não existe — informe um valor válido"
            return

        logger.debug(f"Food detail confirmed: {self.food.description} x {grams}g")
        self.dispatch("on_use_food", self.food, grams)

    def on_use_food(self, food, grams):
        """Evento disparado ao confirmar; o popup de busca fecha este dialog e
        reemite para a MainView, que cuida do cálculo e do preenchimento."""
