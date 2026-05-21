from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup

def show_error(title: str, message: str) -> None:
    content = BoxLayout(orientation="vertical", padding=10, spacing=10)
    content.add_widget(Label(text=message))
    close_btn = Button(text="OK", size_hint_y=None, height=40)
    popup = Popup(title=title, content=content, size_hint=(0.55, 0.3))
    close_btn.bind(on_press=popup.dismiss)
    content.add_widget(close_btn)
    popup.open()