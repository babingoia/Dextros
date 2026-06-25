from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.lang import Builder

from logging import getLogger
from presentation.kivy.ui.widgets.loader import CardWidget
from presentation.kivy.ui.widgets.loader import Border


Builder.load_file("presentation/kivy/ui/widgets/graphs/matrix_cell.kv")
logger = getLogger()


class MatrixCell(Border):

    is_empty = BooleanProperty(True)
    is_header = BooleanProperty(False)
    dextro_text = StringProperty("")
    card_reference = ObjectProperty(None, allownone=True)


    def _show_card_details(self):
        logger.debug(f"Showing details for card: {self.card_reference}")
        
        content = CardWidget(self.card_reference)

        width = min(dp(500), Window.width * 0.9)
        height = min(dp(450), Window.height * 0.9)

        popup = Popup(title="Card Details",
                     content=content, 
                     size_hint=(None, None),
                     size=(width, height)
                     )

        content.popup = popup
        popup.open()