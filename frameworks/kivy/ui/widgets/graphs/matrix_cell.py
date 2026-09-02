from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, NumericProperty
from kivy.metrics import sp
from kivy.lang import Builder
from logging import getLogger

from frameworks.kivy.ui.widgets.loader import CardWidget, Border
from frameworks.kivy.ui.widgets.popup.dialog import AppDialog, DialogMessage

Builder.load_file("frameworks/kivy/ui/widgets/graphs/matrix_cell.kv")

logger = getLogger(__name__)


class MatrixCell(Border):
    is_empty = BooleanProperty(True)
    is_header = BooleanProperty(False)

    dextro_text = StringProperty("")

    delete_callback = ObjectProperty(None, allownone=True)
    card_reference = ObjectProperty(None, allownone=True)

    # Fonte proporcional ao tamanho da célula (zoom)
    cell_font_size = NumericProperty(sp(14))
    font_height_ratio = NumericProperty(0.38)
    font_width_ratio = NumericProperty(0.16)
    min_cell_font_size = NumericProperty(sp(10))
    max_cell_font_size = NumericProperty(sp(24))

    def _show_card_details(self):
        if self.is_empty or self.is_header or not self.card_reference:
            return

        logger.debug(f"Showing details for card: {self.card_reference.get('card_id')}")
        self._build_details_dialog().open()

    def _build_details_dialog(self):
        dialog = AppDialog(
            title="Detalhes",
            content=CardWidget(self.card_reference),
        )
        dialog.set_buttons([
            ("Excluir", "danger", lambda *a: self._switch_to_confirm(dialog)),
            ("Voltar", "primary", lambda *a: dialog.dismiss()),
        ])
        return dialog

    def _switch_to_confirm(self, dialog):
        card_id = self.card_reference.get("card_id")
        dialog.auto_height = True
        dialog.title_text = "Confirmar exclusão"
        dialog.set_content(DialogMessage(
            text="Excluir este registro? Essa ação não pode ser desfeita."
        ))
        dialog.set_buttons([
            ("Excluir", "danger", lambda *a: self._confirm_delete(dialog, card_id)),
            ("Cancelar", "primary", lambda *a: self._switch_to_details(dialog)),
        ])

    def _switch_to_details(self, dialog):
        dialog.auto_height = False
        dialog.title_text = "Detalhes"
        dialog.set_content(CardWidget(self.card_reference))
        dialog.set_buttons([
            ("Excluir", "danger", lambda *a: self._switch_to_confirm(dialog)),
            ("Voltar", "primary", lambda *a: dialog.dismiss()),
        ])

    def _confirm_delete(self, dialog, card_id):
        dialog.dismiss()
        self._on_delete_clicked(card_id)

    def _on_delete_clicked(self, card_id: str):
        logger.debug(f"MatrixCell calling delete callback for card_id: {card_id}")
        if self.delete_callback:
            self.delete_callback(card_id)
        else:
            logger.warning("Delete callback não foi injetado na MatrixCell!")

    def on_delete_request(self, card_id: str):
        pass