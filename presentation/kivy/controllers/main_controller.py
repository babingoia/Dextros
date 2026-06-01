from presentation.kivy.controllers.SessionCache import SessionCache
from core.value_objects.Time import Time
from core.value_objects.Card import Card
from presentation.kivy.controllers.matrix_controller import MatrixController
from presentation.kivy.ui.main_view import MainView


class MainController():

    def __init__(self, cards_on_session=SessionCache(), **kwargs):
        super().__init__(**kwargs)

        self.cards_on_session = cards_on_session

        self.main_view = MainView()
        self.matrix_controller = MatrixController(self.main_view.get_data()['date_hour_matrix'])

        self.time = Time()
        self.main_view.horarios_disponiveis = self.time.get_horarios()
        self.main_view.horario_atual = self.time.get_horario_now()

        self.main_view.bind(on_save_request=self._handle_save_request)
    

    def _handle_save_request(self, instance, *args):
        print("handling save request")
        raw_data = self.main_view.get_data()
        new_card = self._create_card(raw_data)
        self._save_card(new_card)


    def _create_card(self, data: dict[str, str]) -> Card:
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
        print("saving card...")
        self.cards_on_session.add_card(card)
    

    def throw_exception(self, message: str) -> None:
        self.main_view.show_error(message)