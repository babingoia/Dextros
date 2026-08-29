from kivymd.uix.pickers import MDDatePicker
from datetime import date
from logging import getLogger

logger = getLogger(__name__)


class DatePicker(MDDatePicker):

    __events__ = ("on_date_save",)

    def __init__(self, selected_date, on_date_selected, **kwargs):
        logger.debug(f"Initializing DatePicker with selected_date: {selected_date}")
        super().__init__(**kwargs)
        self.title = "Escolha a Data"
        self.selected_date = selected_date
        self.on_date_selected = on_date_selected

           
    def show_date_picker(self):
        self.bind(on_save=self.on_date_save, on_cancel=self.on_cancel)
        self.open()

    
    def on_date_selected(self, date_str):
        logger.debug(f"Date selected callback: {date_str}")


    def on_date_save(self, instance, value: date, *args):
        logger.debug(f"Date selected: {value}")

        if value == [] or not value:
            return

        self.selected_date = value.strftime("%Y-%m-%d")
        self.on_date_selected(self.selected_date)
        self.dismiss()


    def on_cancel(self, instance, *args):
        logger.debug("Date selection cancelled.")
        self.dismiss()