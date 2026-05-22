from kivymd.uix.pickers import MDDatePicker
from core.value_objects.Date import Date


class DatePicker(MDDatePicker):
    def __init__(self, on_date_selected, **kwargs):
        super().__init__(**kwargs)
        self.title = "Select Date"
        self.date = Date()
        self.on_date_selected = on_date_selected

           
    def show_date_picker(self):
        self.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        self.open()

    
    def on_date_selected(self, date_str):
        self.date.set_date(date_str)


    def on_save(self, instance, value, *args):
        if value == [] or not value:
            return

        self.date.set_date(value)
        self.on_date_selected(self.date)
        self.dismiss()
        print(f"Selected date: {self.date.to_string()}")


    def on_cancel(self, instance, *args):
        print(self.date.to_string())
        self.dismiss()