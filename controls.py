import os, sys, subprocess
import configparser
import time
import re
from PIL import Image, ImageTk
import cv2
from lib.CameraControl import CameraControl
from lib.pyinstaller_helper import resource_path, user_path
from tkinter import Button, PhotoImage, Label, LabelFrame, Menu, Tk
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

        self.message = Label(self.root, text="", anchor="center")
        self.message.grid(row=0, column=0)

        self.menubar = Menu(self.root)
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Settings", command=self.open_settings)
        self.filemenu.add_command(label="Reload", command=self.reload)
        self.menubar.add_cascade(label="File", menu=self.filemenu)

        self.reload()
        self.root.config(menu=self.menubar)
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
                frame.grid(row=idx + 1, column=0, padx=10, pady=10)

        except Exception as err:
            self.message.configure(text=f'Error: {err}')

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
        camera_control = CameraControls(self.root, name=name, host=host, port=port, username=username,
                                        password=password)
        self.cameras.append(camera_control)
        camera_control.initialize_preview()


class CameraControls:
    def __init__(self, tk_root, name='', host='', port=80, username='admin', password=''):

        self.name = name
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.camera = None
        self.enabled = False

        self.zoom_speed = 40
        self.zoom_speed_fast = 80

        self.move_speed = 30
        self.move_speed_fast = 80

        self.cap = None
        self.preview_height = 200
        self.preview_fps = 20

        self.frame = LabelFrame(tk_root, text=self.name)

        self.preview = Label(self.frame, height=self.preview_height)
        self.preview.grid(row=0, column=0, rowspan=6)

        self.up_photo_fast = PhotoImage(file=resource_path(os.path.join('assets', 'up-fast.png')))
        self.up_button_fast = Button(self.frame, image=self.up_photo_fast, height=40, width=40, state="disabled",
                                     border=0)
        self.up_button_fast.bind("<ButtonPress>", lambda evt: self.move_up(self.move_speed_fast))
        self.up_button_fast.bind("<ButtonRelease>", self.stop_move)
        self.up_button_fast.grid(row=0, column=5, padx=0, pady=0)

        self.up_photo = PhotoImage(file=resource_path(os.path.join('assets', 'up.png')))
        self.up_button = Button(self.frame, image=self.up_photo, height=40, width=40, state="disabled", border=0)
        self.up_button.bind("<ButtonPress>", lambda evt: self.move_up(self.move_speed))
        self.up_button.bind("<ButtonRelease>", self.stop_move)
        self.up_button.grid(row=1, column=5, padx=0, pady=0)

        self.down_photo = PhotoImage(file=resource_path(os.path.join('assets', 'down.png')))
        self.down_button = Button(self.frame, image=self.down_photo, height=40, width=40, state="disabled", border=0)
        self.down_button.bind("<ButtonPress>", lambda evt: self.move_down(self.move_speed))
        self.down_button.bind("<ButtonRelease>", self.stop_move)
        self.down_button.grid(row=3, column=5, padx=0, pady=0)

        self.down_photo_fast = PhotoImage(file=resource_path(os.path.join('assets', 'down-fast.png')))
        self.down_button_fast = Button(self.frame, image=self.down_photo_fast, height=40, width=40, state="disabled",
                                       border=0)
        self.down_button_fast.bind("<ButtonPress>", lambda evt: self.move_down(self.move_speed_fast))
        self.down_button_fast.bind("<ButtonRelease>", self.stop_move)
        self.down_button_fast.grid(row=4, column=5, padx=0, pady=0)

        self.left_photo_fast = PhotoImage(file=resource_path(os.path.join('assets', 'left-fast.png')))
        self.left_button_fast = Button(self.frame, image=self.left_photo_fast, height=40, width=40, state="disabled",
                                       border=0)
        self.left_button_fast.bind("<ButtonPress>", lambda evt: self.move_left(self.move_speed_fast))
        self.left_button_fast.bind("<ButtonRelease>", self.stop_move)
        self.left_button_fast.grid(row=2, column=2, padx=0, pady=0)

        self.left_photo = PhotoImage(file=resource_path(os.path.join('assets', 'left.png')))
        self.left_button = Button(self.frame, image=self.left_photo, height=40, width=40, state="disabled", border=0)
        self.left_button.bind("<ButtonPress>", lambda evt: self.move_left(self.move_speed))
        self.left_button.bind("<ButtonRelease>", self.stop_move)
        self.left_button.grid(row=2, column=3, padx=0, pady=0)

        self.right_photo = PhotoImage(file=resource_path(os.path.join('assets', 'right.png')))
        self.right_button = Button(self.frame, image=self.right_photo, height=40, width=40, state="disabled", border=0)
        self.right_button.bind("<ButtonPress>", lambda evt: self.move_right(self.move_speed))
        self.right_button.bind("<ButtonRelease>", self.stop_move)
        self.right_button.grid(row=2, column=6, padx=0, pady=0)

        self.right_photo_fast = PhotoImage(file=resource_path(os.path.join('assets', 'right-fast.png')))
        self.right_button_fast = Button(self.frame, image=self.right_photo_fast, height=40, width=40, state="disabled",
                                        border=0)
        self.right_button_fast.bind("<ButtonPress>", lambda evt: self.move_right(self.move_speed_fast))
        self.right_button_fast.bind("<ButtonRelease>", self.stop_move)
        self.right_button_fast.grid(row=2, column=7, padx=0, pady=0)

        self.plus_photo_fast = PhotoImage(file=resource_path(os.path.join('assets', 'plus-fast.png')))
        self.zoom_in_button_fast = Button(self.frame, image=self.plus_photo_fast, height=40, width=40, state="disabled",
                                          border=0)
        self.zoom_in_button_fast.bind("<ButtonPress>", lambda evt: self.zoom_in(self.zoom_speed_fast))
        self.zoom_in_button_fast.bind("<ButtonRelease>", self.stop_move)
        self.zoom_in_button_fast.grid(row=0, column=1, padx=0, pady=0)

        self.plus_photo = PhotoImage(file=resource_path(os.path.join('assets', 'plus.png')))
        self.zoom_in_button = Button(self.frame, image=self.plus_photo, height=40, width=40, state="disabled", border=0)
        self.zoom_in_button.bind("<ButtonPress>", lambda evt: self.zoom_in(self.zoom_speed))
        self.zoom_in_button.bind("<ButtonRelease>", self.stop_move)
        self.zoom_in_button.grid(row=1, column=1, padx=0, pady=0)

        self.minus_photo = PhotoImage(file=resource_path(os.path.join('assets', 'minus.png')))
        self.zoom_out_button = Button(self.frame, image=self.minus_photo, height=40, width=40, state="disabled",
                                      border=0)
        self.zoom_out_button.bind("<ButtonPress>", lambda evt: self.zoom_out(self.zoom_speed))
        self.zoom_out_button.bind("<ButtonRelease>", self.stop_move)
        self.zoom_out_button.grid(row=3, column=1, padx=0, pady=0)

        self.minus_photo_fast = PhotoImage(file=resource_path(os.path.join('assets', 'minus-fast.png')))
        self.zoom_out_button_fast = Button(self.frame, image=self.minus_photo_fast, height=40, width=40,
                                           state="disabled", border=0)
        self.zoom_out_button_fast.bind("<ButtonPress>", lambda evt: self.zoom_out(self.zoom_speed_fast))
        self.zoom_out_button_fast.bind("<ButtonRelease>", self.stop_move)
        self.zoom_out_button_fast.grid(row=4, column=1, padx=0, pady=0)

        self.message = Label(self.frame, text="", anchor="center")
        self.message.grid(row=5, column=1, columnspan=6)

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

    def move_left(self, speed):
        if self.enabled:
            self.camera.move(-1 * round(speed / 100, 1), 0)

    def move_right(self, speed):
        if self.enabled:
            self.camera.move(round(speed / 100, 1), 0)

    def move_up(self, speed):
        if self.enabled:
            self.camera.move(0, round(speed / 100, 1))

    def move_down(self, speed):
        if self.enabled:
            self.camera.move(0, -1 * round(speed / 100, 1))

    def stop_move(self, speed):
        if self.enabled:
            self.camera.stop()

    def zoom_in(self, speed):
        if self.enabled:
            self.camera.zoom(round(speed / 100, 1))

    def zoom_out(self, speed):
        if self.enabled:
            self.camera.zoom(round(-1 * speed / 100, 1))

    def enable_all(self):
        self.up_button.configure(state="normal")
        self.up_button_fast.configure(state="normal")
        self.down_button.configure(state="normal")
        self.down_button_fast.configure(state="normal")
        self.left_button.configure(state="normal")
        self.left_button_fast.configure(state="normal")
        self.right_button.configure(state="normal")
        self.right_button_fast.configure(state="normal")
        self.zoom_in_button.configure(state="normal")
        self.zoom_in_button_fast.configure(state="normal")
        self.zoom_out_button.configure(state="normal")
        self.zoom_out_button_fast.configure(state="normal")
        self.enabled = True

    def initialize_preview(self):
        if self.cap:
            self.cap.release()
            time.sleep(0.2)
        self.cap = cv2.VideoCapture(
            "rtsp://demo:demo@ipvmdemo.dyndns.org:5541/onvif-media/media.amp?profile=profile_1_h264&sessiontimeout=60&streamtype=unicast")
        self.grab_frames()
        self.show_frames()

    def grab_frames(self):
        self.cap.grab()
        self.frame.after(10, self.grab_frames)

    def show_frames(self):
        cv2image = cv2.cvtColor(self.cap.retrieve()[1], cv2.COLOR_BGR2RGB)
        ratio = cv2image.shape[0] / cv2image.shape[1]
        width = int(self.preview_height / ratio)
        resized = cv2.resize(cv2image, (width, self.preview_height), interpolation=cv2.INTER_AREA)
        img = Image.fromarray(resized)
        imgtk = ImageTk.PhotoImage(image=img)
        self.preview.imgtk = imgtk
        self.preview.configure(image=imgtk)
        speed = int(1000 / self.preview_fps)
        self.preview.after(speed, self.show_frames)


if __name__ == '__main__':
    cc = Controller()
