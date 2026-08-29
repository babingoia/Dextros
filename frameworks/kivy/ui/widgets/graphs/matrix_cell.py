# framework/kivy/ui/widgets/graphs/matrix_cell.py
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.lang import Builder
from logging import getLogger
import frameworks.kivy.ui.app_theme as app_theme

from frameworks.kivy.ui.widgets.loader import CardWidget, Border

Builder.load_file("frameworks/kivy/ui/widgets/graphs/matrix_cell.kv")
logger = getLogger(__name__)


class MatrixCell(Border):
    is_empty = BooleanProperty(True)
    is_header = BooleanProperty(False)
    dextro_text = StringProperty("")
    card_reference = ObjectProperty(None, allownone=True)

    # Declara o evento customizado que vai borbulhar para o Controller
    __events__ = ("on_delete_request",)

    def _show_card_details(self):
        # Só abre popup se for um card real
        if self.is_empty or self.is_header or not self.card_reference:
            return

        logger.debug(f"Showing details for card: {self.card_reference.get('card_id')}")
        
        # Injeta o callback de deleção
        content = CardWidget(self.card_reference, on_delete_callback=self._on_delete_clicked)

        width = min(dp(500), Window.width * 0.9)
        height = min(dp(450), Window.height * 0.9)

        popup = Popup(
            title="Card Details",
            content=content,
            size_hint=(None, None),
            size=(width, height),
            title_color=app_theme.color("text_primary"),
            separator_color=app_theme.color("border_focus"),
        )

        # Dá acesso ao popup para o CardWidget conseguir fechar depois de deletar
        content.popup = popup
        popup.open()

    def _on_delete_clicked(self, card_id: str):
        """Recebe o clique do CardWidget e dispara o evento para fora da RecycleView."""
        logger.debug(f"MatrixCell dispatching delete request for card_id: {card_id}")
        self.dispatch("on_delete_request", card_id)

    def on_delete_request(self, card_id: str):
        """Handler padrão obrigatório para eventos Kivy. O Controller vai interceptar."""
        pass