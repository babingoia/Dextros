from logging import getLogger
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ListProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

import frameworks.kivy.ui.app_theme as app_theme
from infrastructure.path_provider_service import get_asset_path
from frameworks.kivy.ui.widgets.popup.dialog import AppDialog
from frameworks.kivy.ui.widgets.pickers.food_detail_popup import (
    FoodDetailContent,
    format_nutrient_value,
)

Builder.load_file(get_asset_path('frameworks/kivy/ui/widgets/pickers/food_search_popup.kv'))

logger = getLogger(__name__)


class FoodResultRow(Button):
    """Linha de resultado da busca: descrição + categoria + valores por 100g.
    Viewclass da RecycleView — as instâncias são recicladas, então o estado
    mora nos dados (dict por linha) e não no widget. O toque abre o popup de
    detalhes do alimento via row_callback(food)."""
    food = ObjectProperty(None)
    row_callback = ObjectProperty(None)
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
            f"{food.category} · CHO {format_nutrient_value(food.carbohydrate_g)} g · "
            f"Gord {format_nutrient_value(food.fat_g)} g (por 100 g)"
        )


class FoodSearchContent(BoxLayout):
    """Conteúdo do popup de busca na Tabela TACO: busca + categoria + lista
    RecycleView. A lista abre com a tabela COMPLETA (decisão de produto, mobile
    first) e filtra conforme o usuário digita; o toque numa linha abre o popup
    de detalhes, onde ficam a quantidade e o botão Adicionar. A fonte de dados é
    injetada (search_handler callable) — o widget não conhece router nem use case.

    Adicionar FECHA só o popup de detalhes: quem come mais de um alimento volta
    pra lista e adiciona o próximo. A linha de total no rodapé (accumulated_text)
    mostra o que já foi somado ao registro a cada Adicionar."""

    __events__ = ("on_use_food",)

    categories = ListProperty([])
    accumulated_text = StringProperty("")

    SEARCH_DEBOUNCE_SECONDS = 0.3

    def __init__(self, categories=None, search_handler=None, **kwargs):
        super().__init__(**kwargs)
        self.categories = categories or []
        self.search_handler = search_handler
        self._search_scheduled = None
        self._detail_dialog = None
        # Primeira população na próxima frame: abre com a tabela inteira navegável
        Clock.schedule_once(lambda dt: self.search(), 0)

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
        """Alimenta a RecycleView. RecycleView recicla as views fora da tela:
        597 linhas custam o mesmo que as ~8 visíveis. Cada linha carrega o Food
        e o callback — o estado é dos dados, não do widget reciclado."""
        self.ids.results_rv.data = [
            {"food": food, "row_callback": self._open_food_detail}
            for food in foods
        ]

        empty = self.ids.empty_state
        empty.height = 0 if foods else app_theme.widget("input_height")
        empty.opacity = 0 if foods else 1

    def _open_food_detail(self, food):
        """Toque na linha: abre o popup de detalhes empilhado sobre a busca."""
        if food is None:
            return
        detail = FoodDetailContent(food=food)
        detail.bind(on_use_food=self._on_detail_confirm)
        self._detail_dialog = AppDialog(
            title="Detalhes do alimento",
            auto_height=True,
            content=detail,
            buttons=[("Fechar", "primary", lambda *a: self._close_detail())],
        )
        self._detail_dialog.open()

    def _close_detail(self, *args):
        if self._detail_dialog is not None:
            self._detail_dialog.dismiss()
            self._detail_dialog = None

    def close_detail(self):
        """Chamado quando o dialog de busca fecha (Fechar) — o detalhe
        empilhado não pode sobreviver sem o pai."""
        self._close_detail()

    def set_accumulated(self, carb_text, fat_text):
        """Atualiza a linha de total do registro (rodapé do popup). Recebe os
        textos crus dos campos do formulário — o mesmo que o usuário vê lá.
        Sem nada acumulado, a linha some."""
        parts = []
        if carb_text and carb_text.strip():
            parts.append(f"CHO {carb_text.strip()} g")
        if fat_text and fat_text.strip():
            parts.append(f"Gordura {fat_text.strip()} g")
        self.accumulated_text = ("No registro: " + " · ".join(parts)) if parts else ""

    def _on_detail_confirm(self, content, food, grams):
        self._close_detail()
        self.dispatch("on_use_food", food, grams)

    def on_use_food(self, food, grams):
        """Evento disparado ao confirmar; a MainView cuida do cálculo e do preenchimento."""
