import os, sys, subprocess
import configparser
import re
from lib.CameraControl import CameraControl
from lib.pyinstaller_helper import resource_path, user_path
from tkinter import Button, PhotoImage, Label, LabelFrame, Tk
from onvif.exceptions import ONVIFError


class Controller:
    def __init__(self):
        self.app_name = 'Camera Control'
        self.settings_filename = user_path(self.app_name, 'settings.ini')
        self.config = None
        self.cameras = []

        self.root = Tk()
        self.root.title("Camera Control")
        self.root.iconbitmap(resource_path(os.path.join('assets', 'favicon.ico')))

        settings_photo = PhotoImage(file=resource_path(os.path.join('assets', 'settings.png')))
        self.settings_button = Button(self.root, image=settings_photo, height=24, width=24,
                                      command=self.open_settings)
        self.settings_button.grid(row=1, column=0, padx=5, pady=5, ipadx=5, ipady=5)

        self.message = Label(self.root, text="", anchor="center")
        self.message.grid(row=1, column=1, columnspan=5)

        try:
            self.load_settings()

            cameras_sections = self.get_camera_sections()
            for section in cameras_sections:
                self.initialize_camera(section)

            for idx, camera in enumerate(self.cameras):
                frame = camera.get_frame()
                frame.grid(row=idx+1, column=1)

        except Exception as err:
            self.message.configure(text=f'Error: {err}')

        self.root.mainloop()

    def default_settings(self):
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

        self.config = configparser.ConfigParser()
        self.config.read(self.settings_filename)

    def get_camera_sections(self):
        cameras = []
        sections = list(self.config.sections())
        for section in sections:
            p = re.search(r"^Camera \d+$", section)
            if p:
                cameras.append(section)

        return cameras

    def initialize_camera(self, section):
        name = self.config.get(section, 'name')
        host = self.config.get(section, 'host')
        port = self.config.get(section, 'port')
        username = self.config.get(section, 'username')
        password = self.config.get(section, 'password')
        camera_control = CameraControls(self.root, name=name, host=host,port=port,username=username,password=password)
        self.cameras.append(camera_control)


class CameraControls:
    def __init__(self, tk_root, name='', host='', port=80, username='admin', password=''):

        self.name = name
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.camera = None

        self.zoom_speed = 50
        self.move_speed = 50

        self.frame = LabelFrame(tk_root, text=self.name)

        self.up_photo = PhotoImage(file=resource_path(os.path.join('assets', 'up.png')))
        self.up_button = Button(self.frame, image=self.up_photo, height=24, width=24, state="disabled")
        self.up_button.bind("<ButtonPress>", self.move_up)
        self.up_button.bind("<ButtonRelease>", self.move_up)
        self.up_button.grid(row=1, column=3, padx=5, pady=5, ipadx=5, ipady=5)

        self.down_photo = PhotoImage(file=resource_path(os.path.join('assets', 'down.png')))
        self.down_button = Button(self.frame, image=self.down_photo, height=24, width=24, state="disabled")
        self.down_button.bind("<ButtonPress>", self.move_down)
        self.down_button.bind("<ButtonRelease>", self.move_down)
        self.down_button.grid(row=3, column=3, padx=5, pady=5, ipadx=5, ipady=5)

        self.left_photo = PhotoImage(file=resource_path(os.path.join('assets', 'left.png')))
        self.left_button = Button(self.frame, image=self.left_photo, height=24, width=24, state="disabled")
        self.left_button.bind("<ButtonPress>", self.move_left)
        self.left_button.bind("<ButtonRelease>", self.move_left)
        self.left_button.grid(row=2, column=2, padx=5, pady=5, ipadx=5, ipady=5)

        self.right_photo = PhotoImage(file=resource_path(os.path.join('assets', 'right.png')))
        self.right_button = Button(self.frame, image=self.right_photo, height=24, width=24, state="disabled")
        self.right_button.bind("<ButtonPress>", self.move_right)
        self.right_button.bind("<ButtonRelease>", self.stop_move)
        self.right_button.grid(row=2, column=4, padx=5, pady=5, ipadx=5, ipady=5)

        self.plus_photo = PhotoImage(file=resource_path(os.path.join('assets', 'plus.png')))
        self.zoom_in_button = Button(self.frame, image=self.plus_photo, height=24, width=24, state="disabled")
        self.zoom_in_button.bind("<ButtonPress>", self.zoom_in)
        self.zoom_in_button.bind("<ButtonRelease>", self.stop_move)
        self.zoom_in_button.grid(row=2, column=0, padx=5, pady=5, ipadx=5, ipady=5)

        self.minus_photo = PhotoImage(file=resource_path(os.path.join('assets', 'minus.png')))
        self.zoom_out_button = Button(self.frame, image=self.minus_photo, height=24, width=24, state="disabled")
        self.zoom_out_button.bind("<ButtonPress>", self.zoom_out)
        self.zoom_out_button.bind("<ButtonRelease>", self.stop_move)
        self.zoom_out_button.grid(row=3, column=0, padx=5, pady=5, ipadx=5, ipady=5)

        self.message = Label(self.frame, text="", anchor="center")
        self.message.grid(row=4, column=0, columnspan=5)

        try:
            self.connect_to_camera()
            self.enable_all()
        except ONVIFError:
            self.message.configure(text=f'Error: Cannot connect to {self.name}')
        except Exception as err:
            self.message.configure(text=f'Error: {err}')

    def get_frame(self):
        return self.frame

    def connect_to_camera(self):
        self.camera = CameraControl(host=self.host, port=self.port, username=self.username, password=self.password)
        self.camera.setup()

    def move_left(self, evt):
        self.camera.move(-1 * round(self.move_speed / 100, 1), 0)

    def move_right(self, evt):
        self.camera.move(round(self.move_speed / 100, 1), 0)

    def move_up(self, evt):
        self.camera.move(0, round(self.move_speed / 100, 1))

    def move_down(self, evt):
        self.camera.move(0, -1 * round(self.move_speed / 100, 1))

    def stop_move(self, evt):
        self.camera.stop()

    def zoom_in(self, evt):
        self.camera.zoom(round(self.zoom_speed / 100, 1))

    def zoom_out(self, evt):
        self.camera.zoom(round(-1 * self.zoom_speed / 100, 1))

    def enable_all(self):
        self.up_button.configure(state="normal")
        self.down_button.configure(state="normal")
        self.left_button.configure(state="normal")
        self.right_button.configure(state="normal")
        self.zoom_in_button.configure(state="normal")
        self.zoom_out_button.configure(state="normal")


if __name__ == '__main__':
    cc = Controller()
