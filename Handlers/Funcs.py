from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
import os, sys
from kivy.app import App

def show_error(title: str, message: str) -> None:
    content = BoxLayout(orientation="vertical", padding=10, spacing=10)
    content.add_widget(Label(text=message))
    close_btn = Button(text="OK", size_hint_y=None, height=40)
    popup = Popup(title=title, content=content, size_hint=(0.55, 0.3))
    close_btn.bind(on_press=popup.dismiss)
    content.add_widget(close_btn)
    popup.open()


def get_asset_path(relative_path):
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative_path)


def get_data_path(relative_path):
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative_path)


def save_file(filename):
    """Caminho correto em todas as plataformas para arquivos de escrita."""
    from kivy.app import App
    return os.path.join(App.get_running_app().user_data_dir, filename)