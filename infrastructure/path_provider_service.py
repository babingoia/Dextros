import os, sys
from logging import getLogger


logger = getLogger(__name__)


def get_asset_path(relative_path):
    logger.debug(f"Getting asset path for: {relative_path}")
    
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    logger.debug(f"Base path: {base}")
    return os.path.join(base, relative_path)


def get_data_path(relative_path):
    logger.debug(f"Getting data path for: {relative_path}")

    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    logger.debug(f"Base path: {base}")
    return os.path.join(base, relative_path)
