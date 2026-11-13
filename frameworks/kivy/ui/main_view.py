from kivy.properties import StringProperty
from kivy.properties import ListProperty
from datetime import date
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from logging import getLogger
from kivy.factory import Factory

# My files
from frameworks.kivy.ui.widgets.pickers.date_picker import DatePicker
from frameworks.kivy.ui.widgets.graphs.screens.graph_screen import GraphScreen
from frameworks.kivy.ui.widgets.pickers.food_search_popup import FoodSearchContent
from infrastructure.path_provider_service import get_asset_path
from adapters.controllers.dtos.card_view_model import CardViewModel
from adapters.controllers.mappers.mappers import sum_grams_for_input
from frameworks.kivy.ui.widgets.popup.dialog import AppDialog, DialogMessage

Builder.load_file(get_asset_path('frameworks/kivy/ui/main_scene.kv'))
Builder.load_file(get_asset_path('frameworks/kivy/ui/ui_components.kv'))

logger = getLogger(__name__)


class MainView(BoxLayout):
    __events__ = ("on_save_request",)

    available_meals = ListProperty([])
    available_time = ListProperty([])
    available_food_categories = ListProperty([])
    # Default = "nenhum" (opção de UI, não de domínio): o card nasce salvo-sem-refeição
    # em vez de nascer com placeholder inválido (causa do crash ao salvar sem tocar).
    actual_meal = StringProperty("nenhum")
    actual_time = StringProperty("Horário:")
    date_display = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.info("MainView initialized")
        self.date_picker = DatePicker(
            self.date_display,
            on_date_selected=self._update_data_input
        )
        # Handlers injetados pelo MainController (padrão refresh_callback):
        # a UI não conhece router nem use case, só os callables.
        self.food_search_handler = None      # callable(query, category) -> FoodSearchResult
        self.nutrition_calculator = None     # callable(food, grams) -> Meal | None
        self._active_food_search_dialog = None

    def on_save_request(self, *args):
        logger.debug("Save request event triggered with data: %s", args)

    def show_save_confirmation(
        self,
        message: str = "Registro Salvo!",
        title: str = "Salvar"
    ) -> None:
        logger.info("Save confirmation popup displayed")

        dialog = AppDialog(title=title, auto_height=True)
        dialog.set_content(DialogMessage(text=message))
        dialog.set_buttons([
            ("OK", "primary", lambda *a: dialog.dismiss())
        ])
        dialog.open()

    def show_error(self, message: str, title: str = "ERRO") -> None:
        logger.error("Error popup displayed with message: %s", message)

        dialog = AppDialog(title=title, auto_height=True)
        dialog.set_content(DialogMessage(text=message))
        dialog.set_buttons([
            ("OK", "danger", lambda *a: dialog.dismiss())
        ])
        dialog.open()

    def _show_error(self, message: str, title: str = "ERRO") -> None:
        self.show_error(message, title)

    def _choose_date(self) -> None:
        logger.debug("Date picker opened")
        self.date_picker.show_date_picker()

    def _update_data_input(self, date: str) -> None:
        logger.debug("Updating date input with selected date: %s", date)
        self.ids.data_input.text = date

    def get_data(self) -> dict[str, str]:
        logger.debug("Retrieving data from input fields")

        # A seção de nutrição é opt-in: com o toggle desligado, os valores são
        # ignorados mesmo que sobrou texto digitado — o estado do toggle manda.
        nutrition_enabled = self.ids.nutrition_toggle.state == "down"

        data = CardViewModel(
            card_id='',
            card_data=self.ids.data_input.text,
            card_time=self.ids.horario_spinner.text,
            glycemia=self.ids.dextro_input.text,
            long_acting_insulin=self.ids.lenta_input.text,
            short_acting_insulin=self.ids.rapida_input.text,
            exercise={
                'exercise_name': self.ids.exercicio_input.text,
                'intensity': ''
            },
            meal="" if self.ids.meal_value.text.lower() == "nenhum" else self.ids.meal_value.text,
            carbohydrate_g=self.ids.carb_input.text if nutrition_enabled else '',
            fat_g=self.ids.fat_input.text if nutrition_enabled else '',
            observation=self.ids.observacao_input.text,
        )

        return data

    def _open_food_search(self):
        logger.debug("Food search popup opened")

        if self.food_search_handler is None:
            logger.error("food_search_handler not injected — cannot open search")
            self.show_error("Busca de alimentos indisponível nesta sessão.")
            return

        content = FoodSearchContent(
            categories=self.available_food_categories,
            search_handler=self.food_search_handler,
        )
        content.bind(on_use_food=self._on_food_selected)

        self._active_food_search_dialog = AppDialog(
            title="Buscar alimento — Tabela TACO",
            content=content,
            buttons=[
                # "Fechar" e não "Cancelar": o popup é um seletor de alimentos e
                # NÃO fecha quando um alimento é adicionado — cada Adicionar já
                # somou no formulário, não há nada a cancelar.
                ("Fechar", "primary", lambda *a: self._active_food_search_dialog.dismiss()),
            ],
        )
        # O toque na linha abre um popup de detalhes EMPILHADO sobre este dialog.
        # Se a busca fechar, o detalhe não pode sobreviver sem o pai.
        self._active_food_search_dialog.bind(on_dismiss=lambda *a: content.close_detail())
        # Contexto inicial do total: se o registro já tem valores digitados ou buscados,
        # a linha de total nasce mostrando-os (a nutrição é opt-in — com o toggle
        # desligado os campos são ignorados e a linha começa vazia).
        if self.ids.nutrition_toggle.state == "down":
            content.set_accumulated(self.ids.carb_input.text, self.ids.fat_input.text)
        self._active_food_search_dialog.open()

    def _on_food_selected(self, content, food, grams):
        logger.debug(f"Food selected in popup: {food.description} x {grams}g")

        if self.nutrition_calculator is None:
            logger.error("nutrition_calculator not injected — cannot compute nutrition")
            self.show_error("Cálculo de nutrição indisponível nesta sessão.")
            return

        result = self.nutrition_calculator(food, grams)

        if result is None:
            # Alimento sem nenhum dos dois nutrientes na tabela (NA/Tr) —
            # o popup de busca continua aberto para escolher outro alimento.
            self.show_error(
                f"\"{food.description}\" não tem dados de carboidratos ou gorduras "
                "na tabela TACO. Escolha outro alimento ou digite os valores manualmente."
            )
            return

        # A busca destrava a seção sozinha ao preencher
        self.ids.nutrition_toggle.state = "down"

        # UMA refeição é MAIS DE UM alimento: somar ao que já está no campo,
        # nunca substituir. Nutriente ausente na tabela (None) não contribui —
        # o campo mantém o valor que já tinha.
        if result.carbohydrate_g is not None:
            self.ids.carb_input.text = sum_grams_for_input(
                self.ids.carb_input.text, result.carbohydrate_g
            )
        if result.fat_g is not None:
            self.ids.fat_input.text = sum_grams_for_input(
                self.ids.fat_input.text, result.fat_g
            )

        # O popup de busca PERMANECE aberto (só o detalhe fecha, lá no
        # FoodSearchContent): o usuário volta pra lista e adiciona o próximo
        # alimento. A linha de total dá o feedback da soma.
        content.set_accumulated(self.ids.carb_input.text, self.ids.fat_input.text)

    def add_graph_screen(self, name, title, graph_widget, refresh_callback=None):
        """
        Na arquitetura nova: a tela já existe no KV, o GraphScreenContent
        já criou o gráfico internamente. Só precisamos configurar o callback
        e (se necessário) atualizar o título.
        """
        sm = self.ids.screens

        if not sm.has_screen(name):
            logger.warning(f"Tela {name} não encontrada no .kv.")
            return

        screen = sm.get_screen(name)

        # Injeta o callback de lazy load
        if hasattr(screen, 'refresh_callback'):
            screen.refresh_callback = refresh_callback

        # Atualiza o título (se o content tiver a property)
        content = screen.children[0] if screen.children else None
        if content and hasattr(content, 'title'):
            content.title = title

        # Navega para a tela
        sm.current = name

    def _navigate_to(self, name):
        sm = self.ids.screens

        # O Kivy NÃO dispara on_pre_enter se a tela atual já for a de destino.
        # Forçamos o refresh manualmente nesse caso específico.
        if sm.current == name:
            screen = sm.get_screen(name)
            if hasattr(screen, 'refresh_callback') and screen.refresh_callback:
                screen.refresh_callback()
        else:
            sm.current = name

        # Em celular, fecha a navbar lateral após navegar
        if hasattr(self.ids, 'nav_toggle'):
            self.ids.nav_toggle.state = "normal"