import os, sys


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