from logging import getLogger
from datetime import datetime, date, time

from adapters.gateways.i_router import IRouter
from adapters.controllers.dtos.time_view_model import TimeList
from adapters.controllers.dtos.card_view_model import CardViewModel
from frameworks.kivy.ui.main_view import MainView
from frameworks.kivy.controllers.matrix_controller import MatrixController

from kivy.clock import Clock

logger = getLogger(__name__)


_DATA_SOURCE_CONFIG = {
    'date_hour_matrix': "get_hour_date_matrix_data",
    'meal_date_matrix': "get_meal_date_matrix_data"
}


class MainController():

    def __init__(self, router: IRouter, **kwargs):
        logger.info("Initializing MainController")
        
        super().__init__(**kwargs)

        self.router = router

        # Matrizes
        self.main_view = MainView()
        self.date_hour_matrix_controller = MatrixController(self.main_view.ids.date_hour_matrix_container,
                                                            router= self.router, 
                                                            data_souce= _DATA_SOURCE_CONFIG["date_hour_matrix"])

        self.meal_date_matrix_controller = MatrixController(self.main_view.ids.meal_date_matrix_container,
                                                            router=self.router,
                                                            data_souce= _DATA_SOURCE_CONFIG["meal_date_matrix"]
                                                            )

        # Horarios
        self.time: TimeList = self.router.navigate("get_time_list")
        self.main_view.available_time = self.time.not_datetime_time
        self.main_view.actual_time = datetime.now().time().strftime("%H:%M")

        # Data
        self.date: date = datetime.now().date()
        self.main_view.date_display = self.date.strftime("%Y-%m-%d")

        # Refeições
        self.meals = self.router.navigate("get_meal_list")
        self.meals.meal_values.insert(0, "nenhum")
        self.main_view.available_meals = self.meals.meal_values

        # Conectando aos eventos
        self.main_view.bind(on_save_request=self._handle_save_request)
        self.main_view.date_picker.bind(on_date_selected=self._on_date_selected)
        self.main_view.date_picker.bind(on_save=self._on_date_save)
        Clock.schedule_once(self._setup_graph_screen, 0)
    

    def _setup_graph_screen(self, dt):
        """
        Vincula o widget e o callback de lazy load à tela.
        O MainView continua sem saber o que é um MatrixController.
        """
        logger.info("🔗 Vinculando MatrixController à tela 'chart' via MainController...")
        
        self.main_view.add_graph_screen(
            name="chart",
            title="Gráfico",
            graph_widget=self.date_hour_matrix_controller.grid_view,
            refresh_callback=self.date_hour_matrix_controller.on_screen_enter
        )

        self.main_view.add_graph_screen(
        name="meal_date_chart", title="Refeição x Dia",
        graph_widget=self.meal_date_matrix_controller.grid_view,
        refresh_callback=self.meal_date_matrix_controller.on_screen_enter,
        )


    def _handle_save_request(self, instance, *args):
        logger.debug("Save request received from main view.")

        raw_data: CardViewModel = self.main_view.get_data()
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