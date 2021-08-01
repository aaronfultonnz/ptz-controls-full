import os, sys, subprocess
import configparser
import tkinter
import re
from lib.ManagePresets import ManagePresets
from lib.pyinstaller_helper import resource_path, user_path
from tkinter import Label, Menu, Tk
from lib.CameraControl import CameraControl


class Controller:
    def __init__(self):
        self.app_name = 'Camera Control'
        self.settings_filename = user_path(self.app_name, 'settings.ini')
        self.config = None
        self.cameras = []

        self.root = Tk()
        self.root.title("Camera Control")
        self.root.configure(background='white')
        self.root.iconbitmap(resource_path(os.path.join('assets', 'favicon.ico')))

        self.message = Label(self.root, text="", anchor="center", background="white")
        self.message.grid(row=0, column=0)

        self.menubar = Menu(self.root)
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Settings", command=self.open_settings)
        self.filemenu.add_command(label="Reload", command=self.reload)
        self.menubar.add_cascade(label="File", menu=self.filemenu)

        self.presetsmenu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Presets", menu=self.presetsmenu)

        self.move_speed_slow = 40
        self.move_speed_fast = 80
        self.zoom_speed_slow = 30
        self.zoom_speed_fast = 80

        self.reload()
        self.root.config(menu=self.menubar)
        self.root.after(500, self.initialize)  # delay the preview starting for better UX
        self.root.mainloop()

    def reload(self):
        try:
            self.load_settings()
            self.cameras = []
            cameras_sections = self.get_camera_sections()
            for section in cameras_sections:
                self.initialize_camera(section)

            for idx, camera in enumerate(self.cameras):
                frame = camera.get_frame()
                frame.grid(row=idx + 1, column=0, padx=10, pady=10, sticky="nw")

            self.populate_presets_menu()

        except Exception as err:
            self.set_message(f'Error: {err}')

    def initialize(self):
        for camera_control in self.cameras:
            has_started = camera_control.start_camera()
            if has_started:
                camera_control.initialize_preview()

    def populate_presets_menu(self):
        self.presetsmenu.delete(0, tkinter.END)

        for camera_control in self.cameras:
            self.presetsmenu.add_command(label=camera_control.name,
                                         command=lambda camera=camera_control: self.open_preset_window(camera))

    def open_preset_window(self, camera):
        ManagePresets(self.root, camera, self.close_preset_window)

    def close_preset_window(self):
        self.reload()

    def default_settings(self): #@todo replace this
        parser = configparser.ConfigParser()
        config_file = open(self.settings_filename, 'w')
        config_file.write('# Restart the program after changing settings\n')
        parser.add_section('Camera 1')
        parser.set('Camera 1', 'name', 'Camera 1')
        parser.set('Camera 1', 'host', '192.168.x.x')
        parser.set('Camera 1', 'port', '80')
        parser.set('Camera 1', 'username', 'admin')
        parser.set('Camera 1', 'password', '')
        parser.write(config_file)
        config_file.close()

    def open_settings(self):
        if sys.platform == "win32":
            os.startfile(self.settings_filename)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, self.settings_filename])

    def load_settings(self):
        if not os.path.isfile(self.settings_filename):
            self.default_settings()

        self.config = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
        self.config.read(self.settings_filename)

    def get_camera_sections(self):
        cameras = []
        sections = list(self.config.sections())
        for section in sections:
            p = re.search(r"^Camera \d+$", section)
            if p:
                cameras.append(section)

        return cameras

    def get_general_settings(self):
        try:
            self.move_speed_slow = int(self.config['GENERAL']['mode_speed_slow'])
            self.move_speed_fast = int(self.config['GENERAL']['mode_speed_fast'])
            self.zoom_speed_slow = int(self.config['GENERAL']['zoom_speed_slow'])
            self.zoom_speed_fast = int(self.config['GENERAL']['zoom_speed_fast'])
        except Exception:
            self.set_message("Failed to load speed from the configuration file")

    def initialize_camera(self, section):
        camera_control = CameraControl(self.root, config=self.config[section], general=self.config['GENERAL'])
        self.cameras.append(camera_control)

    def set_message(self, message):
        self.message.configure(text=message)
        self.root.update()


if __name__ == '__main__':
    cc = Controller()
