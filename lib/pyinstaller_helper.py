import os
import sys
from appdirs import user_data_dir

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def user_path(application_name, file_name):
    """
    Fetch the users home dir path for configuration files etc.
    If this path does not exist, it is created

    :param application_name: Name of the application
    :return:
    """
    path = user_data_dir('CameraController', 'WebToLife')
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, file_name)
