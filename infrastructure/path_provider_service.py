import os, sys
from logging import getLogger

logger = getLogger(__name__)


def _is_android() -> bool:
    return "P4A_BOOTSTRAP" in os.environ or hasattr(sys, "getandroidapilevel")


def get_asset_path(relative_path):
    if getattr(sys, "frozen", False):            # PyInstaller (desktop)
        base = sys._MEIPASS
    else:                                        # dev desktop + Android (assets no pacote)
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative_path)


def get_data_path(relative_path):
    if _is_android():
        from kivy.app import App
        base = App.get_running_app().user_data_dir  # storage privado, sem permissão
        os.makedirs(base, exist_ok=True)
    elif getattr(sys, "frozen", False):          # PyInstaller (desktop)
        base = os.path.dirname(sys.executable)
    else:                                        # dev desktop
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative_path)