from logging import getLogger
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ListProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

from infrastructure.path_provider_service import get_asset_path

Builder.load_file(get_asset_path('frameworks/kivy/ui/widgets/pickers/food_search_popup.kv'))

logger = getLogger(__name__)


def _format_grams(value) -> str:
    """Formata um valor por 100g para exibição brasileira (vírgula decimal).
    None vira "—" — dado indisponível na tabela é diferente de zero."""
    if value is None:
        return "—"
    return f"{value:.1f}".replace(".", ",")


class FoodResultRow(Button):
    """Linha de resultado da busca: descrição + categoria + valores por 100g."""
    food = ObjectProperty(None)
    row_text = StringProperty("")

    def on_food(self, instance, value):
        """on_food em vez de bind no __init__: o kwarg food é aplicado DENTRO do
        super().__init__(), antes de qualquer bind registrado depois dele — o
        evento dispara e ninguém escuta, e a linha nasce sem texto."""
        self._update_text(value)

    def _update_text(self, *args):
        food = self.food
        if food is None:
            self.row_text = ""
            return
        self.row_text = (
            f"{food.description}\n"
            f"{food.category} · CHO {_format_grams(food.carbohydrate_g)} g · "
            f"Gord {_format_grams(food.fat_g)} g (por 100 g)"
        )


class FoodSearchContent(BoxLayout):
    """Conteúdo do popup de busca na Tabela TACO. A fonte de dados é injetada
    (search_handler callable) — o widget não conhece router nem use case."""

    __events__ = ("on_use_food",)

    categories = ListProperty([])
    selected_food = ObjectProperty(None, allownone=True)
    selected_summary = StringProperty("Selecione um alimento na lista")
    has_results = ListProperty([])

    SEARCH_DEBOUNCE_SECONDS = 0.3

    def __init__(self, categories=None, search_handler=None, **kwargs):
        super().__init__(**kwargs)
        self.categories = categories or []
        self.search_handler = search_handler
        self._search_scheduled = None

    def schedule_search(self, *args):
        """Debounce da digitação: uma busca por rajada de teclas, não uma por caractere."""
        if self._search_scheduled is not None:
            Clock.unschedule(self._search_scheduled)
        self._search_scheduled = Clock.schedule_once(lambda dt: self.search(), self.SEARCH_DEBOUNCE_SECONDS)

    def search(self, *args):
        if self.search_handler is None:
            logger.warning("FoodSearchContent without search_handler — nothing to do")
            return

        query = self.ids.search_input.text
        category = self.ids.category_spinner.text
        logger.debug(f"Food search popup querying: query={query!r} category={category!r}")

        result = self.search_handler(query, category)
        self._populate(result.foods)

    def _populate(self, foods):
        holder = self.ids.results_holder
        holder.clear_widgets()
        self.has_results = foods

        if not foods:
            label = self.ids.empty_state
            holder.add_widget(label)
            return

        for food in foods:
            holder.add_widget(FoodResultRow(food=food, on_release=lambda btn: self.select_food(btn.food)))

    def select_food(self, food):
        if food is None:
            return
        self.selected_food = food
        self.selected_summary = (
            f"{food.description} · CHO {_format_grams(food.carbohydrate_g)} g / "
            f"Gord {_format_grams(food.fat_g)} g por 100 g"
        )

    def confirm(self):
        if self.selected_food is None:
            self.selected_summary = "Selecione um alimento na lista primeiro"
            return

        grams_raw = self.ids.grams_input.text.strip().replace(",", ".")
        if not grams_raw:
            self.selected_summary = "Informe a quantidade consumida em gramas"
            return

        try:
            grams = float(grams_raw)
        except ValueError:
            self.selected_summary = "Quantidade inválida — informe um número (ex.: 150)"
            return

        if grams < 0:
            self.selected_summary = "Quantidade negativa não existe — informe um valor válido"
            return

        logger.debug(f"Food search popup confirmed: {self.selected_food.description} x {grams}g")
        self.dispatch("on_use_food", self.selected_food, grams)

    def on_use_food(self, food, grams):
        """Evento disparado ao confirmar; a MainView cuida do cálculo e do preenchimento."""
