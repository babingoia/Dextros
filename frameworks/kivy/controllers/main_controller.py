from logging import getLogger
from datetime import datetime

from adapters.gateways.i_router import IRouter
from adapters.controllers.dtos.time_view_model import TimeList
from adapters.controllers.dtos.card_view_model import CardViewModel
from frameworks.kivy.controllers.bar_matrix_controller import BarMatrixController
from frameworks.kivy.ui.main_view import MainView
from frameworks.kivy.controllers.matrix_controller import MatrixController

logger = getLogger(__name__)

_DATA_SOURCE_CONFIG = {
    'date_hour_matrix': "get_hour_date_matrix_data",
    'meal_date_matrix': "get_meal_date_matrix_data",
    'average_glycemia_matrix': "get_average_glycemia_matrix_data"
}


class MainController:
    def __init__(self, router: IRouter, **kwargs):
        logger.info("Initializing MainController")
        super().__init__(**kwargs)

        self.router = router

        # MainView continua só instanciando. Tudo vem dos ids do KV.
        self.main_view = MainView()

        # Cada content (view) já é dono do gráfico + zoom + sticky.
        self.date_hour_matrix_controller = MatrixController(
            content=self.main_view.ids.chart_content,
            router=self.router,
            data_source=_DATA_SOURCE_CONFIG["date_hour_matrix"],
        )

        self.meal_date_matrix_controller = MatrixController(
            content=self.main_view.ids.meal_date_content,
            router=self.router,
            data_source=_DATA_SOURCE_CONFIG["meal_date_matrix"],
        )

        self.average_glycemia_matrix_controller = BarMatrixController(
            content=self.main_view.ids.average_glycemia_content,
            router=self.router,
            data_source=_DATA_SOURCE_CONFIG["average_glycemia_matrix"]
        )

        # Lazy load: callback direto na screen, sem passar pelo MainView.
        self.main_view.ids.screens.get_screen("chart").refresh_callback = \
            self.date_hour_matrix_controller.on_screen_enter

        self.main_view.ids.screens.get_screen("meal_date_chart").refresh_callback = \
            self.meal_date_matrix_controller.on_screen_enter
        
        self.main_view.ids.screens.get_screen("average_glycemia_bar_graph").refresh_callback = \
            self.average_glycemia_matrix_controller.on_screen_enter

        # Horarios
        self.time: TimeList = self.router.navigate("get_time_list")
        self.main_view.available_time = self.time.not_datetime_time
        self.main_view.actual_time = datetime.now().time().strftime("%H:%M")

        # Data
        self.date = datetime.now().date()
        self.main_view.date_display = self.date.strftime("%Y-%m-%d")

        # Refeições
        self.meals = self.router.navigate("get_meal_list")
        self.meals.meal_values.insert(0, "nenhum")
        self.main_view.available_meals = self.meals.meal_values

        # Conectando aos eventos
        self.main_view.bind(on_save_request=self._handle_save_request)
        self.main_view.date_picker.bind(on_date_selected=self._on_date_selected)
        self.main_view.date_picker.bind(on_save=self._on_date_save)

    def _handle_save_request(self, instance, *args):
        logger.debug("Save request received from main view.")

        raw_data: CardViewModel = self.main_view.get_data()

        # Como ainda não existe response do router, o popup aqui funciona
        # como feedback simples de clique/disparo do fluxo de salvar.
        self.main_view.show_save_confirmation()

        self.router.navigate("save_card", raw_data)

    def throw_exception(self, message: str) -> None:
        logger.error(f"Exception thrown: {message}")
        self.main_view.show_error(message)

    def _on_date_selected(self):
        logger.debug("Date selected callback triggered.")

    def _on_date_save(self, instance, value, *args):
        logger.debug(f"Date save callback triggered with value: {value}")

        if value == [] or not value:
            return