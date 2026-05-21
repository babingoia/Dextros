from kivymd.uix.pickers import MDDatePicker
from datetime import date, datetime


class Date(MDDatePicker):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Select Date"
        self.date = date.today()
        self.reference = None

    def show_date_picker(self, reference):
        self.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        self.open()
        self.reference = reference

    def on_save(self, instance, value, *args):
        if value == []:
            return

        print(f"Selected date: {value}")
        self.date = value
        self.dismiss()

        self.reference.ids.data_input.text = self.date.strftime("%Y-%m-%d")

    def on_cancel(self, instance, *args):
        print(self.date)
        self.dismiss()

    @staticmethod
    def is_valid_date(date_str: str) -> bool:
        """Valida se a string é uma data válida no formato YYYY-MM-DD."""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
