from logging import getLogger


from presentation.kivy.controllers.SessionCache import SessionCache
from core.value_objects.Time import Time
from core.value_objects.Card import Card
from presentation.kivy.controllers.matrix_controller import MatrixController
from presentation.kivy.ui.main_view import MainView
from core.value_objects.Date import Date


logger = getLogger(__name__)


class MainController():

    def __init__(self, cards_on_session=SessionCache(), **kwargs):
        logger.info("Initializing MainController")
        
        super().__init__(**kwargs)

        self.cards_on_session = cards_on_session

        self.main_view = MainView()
        self.matrix_controller = MatrixController(self.main_view.get_data()['date_hour_matrix'])

        # Horarios
        self.time = Time()
        self.main_view.horarios_disponiveis = self.time.get_horarios()
        self.main_view.horario_atual = self.time.get_horario_now()

        # Data
        self.date: Date = Date()
        self.main_view.date_display = self.date.to_string()

        # Conectando aos eventos
        self.main_view.bind(on_save_request=self._handle_save_request)
        self.main_view.date_picker.bind(on_date_selected=self._on_date_selected)
        self.main_view.date_picker.bind(on_save=self._on_date_save)
    

    def _handle_save_request(self, instance, *args):
        logger.debug("Save request received from main view.")

        raw_data = self.main_view.get_data()
        new_card = self._create_card(raw_data)
        self._save_card(new_card)


    def _create_card(self, data: dict[str, str]) -> Card:
        logger.debug(f"Creating card from data: {data}")

        new_card = Card(
            data=data['data'],
            horario=data['horario'],
            dextro=data['dextro'],
            lenta=data['lenta'],
            rapida=data['rapida'],
            exercicio=data['exercicio'],
            refeicao=data['refeicao'],
            observacao=data['observacao']
        )

        return new_card


    def _save_card(self, card: Card) -> None:
        logger.debug(f"Saving card: {card}")

        self.cards_on_session.add_card(card)
    

    def throw_exception(self, message: str) -> None:
        logger.error(f"Exception thrown: {message}")

        self.main_view.show_error(message)
    

    def _on_date_selected(self):
        logger.debug("Date selected callback triggered.")


    def _on_date_save(self, instance, value, *args):
        logger.debug(f"Date save callback triggered with value: {value}")

        if value == [] or not value:
            return

        self.date.set_date(value)