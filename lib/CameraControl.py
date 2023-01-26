import os
import time
from math import floor
from lib.ONVIFControl import ONVIFControl
from lib.pyinstaller_helper import resource_path
from tkinter import Button, PhotoImage, Label, LabelFrame
from onvif.exceptions import ONVIFError


class CameraControl:
    def __init__(self, tk_root, config, general):
        self.root = tk_root
        self.name = 'Camera' if 'name' not in config else config['name']
        self.host = '' if 'host' not in config else config['host']
        self.port = 80 if 'port' not in config else int(config['port'])
        self.username = '' if 'username' not in config else config['username']
        self.password = '' if 'password' not in config else config['password']
        self.zoom_speed_slow = 40 if 'zoom_speed_slow' not in general else int(general['zoom_speed_slow'])
        self.zoom_speed_fast = 80 if 'zoom_speed_fast' in general else int(general['zoom_speed_fast'])
        self.move_speed_slow = 30 if 'move_speed_slow' in general else int(general['move_speed_slow'])
        self.move_speed_fast = 90 if 'move_speed_fast' not in general else int(general['move_speed_fast'])

        self.ovnif = None
        self.enabled = False
        self.cap = None
        self.preset_buttons = []
        self.last_frame_time = time.time()
        self.thread_running = False

        self.frame = LabelFrame(tk_root, text=self.name, background='white', padx=5, pady=5)

        self.up_photo_fast = PhotoImage(file=resource_path(os.path.join('assets', 'up-fast.png')))
        self.up_button_fast = Button(self.frame, image=self.up_photo_fast, height=40, width=40, state="disabled",
                                     border=0, background='white')
        self.up_button_fast.bind("<ButtonPress>", lambda evt: self.move_up(self.move_speed_fast))
        self.up_button_fast.bind("<ButtonRelease>", self.stop_move)
        self.up_button_fast.grid(row=0, column=5, padx=0, pady=0)

        self.up_photo = PhotoImage(file=resource_path(os.path.join('assets', 'up-slow.png')))
        self.up_button = Button(self.frame, image=self.up_photo, height=40, width=40, state="disabled", border=0,
                                background='white')
        self.up_button.bind("<ButtonPress>", lambda evt: self.move_up(self.move_speed_slow))
        self.up_button.bind("<ButtonRelease>", self.stop_move)
        self.up_button.grid(row=1, column=5, padx=0, pady=0)

        self.down_photo = PhotoImage(file=resource_path(os.path.join('assets', 'down-slow.png')))
        self.down_button = Button(self.frame, image=self.down_photo, height=40, width=40, state="disabled", border=0,
                                  background='white')
        self.down_button.bind("<ButtonPress>", lambda evt: self.move_down(self.move_speed_slow))
        self.down_button.bind("<ButtonRelease>", self.stop_move)
        self.down_button.grid(row=3, column=5, padx=0, pady=0)

        self.down_photo_fast = PhotoImage(file=resource_path(os.path.join('assets', 'down-fast.png')))
        self.down_button_fast = Button(self.frame, image=self.down_photo_fast, height=40, width=40, state="disabled",
                                       border=0, background='white')
        self.down_button_fast.bind("<ButtonPress>", lambda evt: self.move_down(self.move_speed_fast))
        self.down_button_fast.bind("<ButtonRelease>", self.stop_move)
        self.down_button_fast.grid(row=4, column=5, padx=0, pady=0)

        self.left_photo_fast = PhotoImage(file=resource_path(os.path.join('assets', 'left-fast.png')))
        self.left_button_fast = Button(self.frame, image=self.left_photo_fast, height=40, width=40, state="disabled",
                                       border=0, background='white')
        self.left_button_fast.bind("<ButtonPress>", lambda evt: self.move_left(self.move_speed_fast))
        self.left_button_fast.bind("<ButtonRelease>", self.stop_move)
        self.left_button_fast.grid(row=2, column=2, padx=0, pady=0)

        self.left_photo = PhotoImage(file=resource_path(os.path.join('assets', 'left-slow.png')))
        self.left_button = Button(self.frame, image=self.left_photo, height=40, width=40, state="disabled", border=0,
                                  background='white')
        self.left_button.bind("<ButtonPress>", lambda evt: self.move_left(self.move_speed_slow))
        self.left_button.bind("<ButtonRelease>", self.stop_move)
        self.left_button.grid(row=2, column=3, padx=0, pady=0)

        self.right_photo = PhotoImage(file=resource_path(os.path.join('assets', 'right-slow.png')))
        self.right_button = Button(self.frame, image=self.right_photo, height=40, width=40, state="disabled", border=0,
                                   background='white')
        self.right_button.bind("<ButtonPress>", lambda evt: self.move_right(self.move_speed_slow))
        self.right_button.bind("<ButtonRelease>", self.stop_move)
        self.right_button.grid(row=2, column=6, padx=0, pady=0)

        self.right_photo_fast = PhotoImage(file=resource_path(os.path.join('assets', 'right-fast.png')))
        self.right_button_fast = Button(self.frame, image=self.right_photo_fast, height=40, width=40, state="disabled",
                                        border=0, background='white')
        self.right_button_fast.bind("<ButtonPress>", lambda evt: self.move_right(self.move_speed_fast))
        self.right_button_fast.bind("<ButtonRelease>", self.stop_move)
        self.right_button_fast.grid(row=2, column=7, padx=0, pady=0)

        self.plus_photo_fast = PhotoImage(file=resource_path(os.path.join('assets', 'plus-fast.png')))
        self.zoom_in_button_fast = Button(self.frame, image=self.plus_photo_fast, height=40, width=40, state="disabled",
                                          border=0, background='white')
        self.zoom_in_button_fast.bind("<ButtonPress>", lambda evt: self.zoom_in(self.zoom_speed_fast))
        self.zoom_in_button_fast.bind("<ButtonRelease>", self.stop_move)
        self.zoom_in_button_fast.grid(row=0, column=1, padx=0, pady=0)

        self.plus_photo = PhotoImage(file=resource_path(os.path.join('assets', 'plus.png')))
        self.zoom_in_button = Button(self.frame, image=self.plus_photo, height=40, width=40, state="disabled", border=0,
                                     background='white')
        self.zoom_in_button.bind("<ButtonPress>", lambda evt: self.zoom_in(self.zoom_speed_slow))
        self.zoom_in_button.bind("<ButtonRelease>", self.stop_move)
        self.zoom_in_button.grid(row=1, column=1, padx=0, pady=0)

        self.minus_photo = PhotoImage(file=resource_path(os.path.join('assets', 'minus.png')))
        self.zoom_out_button = Button(self.frame, image=self.minus_photo, height=40, width=40, state="disabled",
                                      border=0, background='white')
        self.zoom_out_button.bind("<ButtonPress>", lambda evt: self.zoom_out(self.zoom_speed_slow))
        self.zoom_out_button.bind("<ButtonRelease>", self.stop_move)
        self.zoom_out_button.grid(row=3, column=1, padx=0, pady=0)

        self.minus_photo_fast = PhotoImage(file=resource_path(os.path.join('assets', 'minus-fast.png')))
        self.zoom_out_button_fast = Button(self.frame, image=self.minus_photo_fast, height=40, width=40,
                                           state="disabled", border=0, background='white')
        self.zoom_out_button_fast.bind("<ButtonPress>", lambda evt: self.zoom_out(self.zoom_speed_fast))
        self.zoom_out_button_fast.bind("<ButtonRelease>", self.stop_move)
        self.zoom_out_button_fast.grid(row=4, column=1, padx=0, pady=0)

        self.message = Label(self.frame, text="", anchor="center", background='white')
        self.message.grid(row=5, column=2, columnspan=8)

    def start_camera(self):
        try:
            self.set_message('Connecting to camera')
            self.connect_to_camera()
            self.setup_presets()
            self.enable_all()
            self.set_message('')
            self.enabled = True
            return True
        except ONVIFError:
            self.set_message(f'Error: Cannot connect to {self.name}')
            return False
        except Exception as err:
            self.set_message(f'Error: {err}')
            return False

    def setup_presets(self):
        start_column = 8  # first column to start drawing the preset buttons
        presets_per_column = 5  # number of presets per column

        presets = self.ovnif.preset_list()
        self.preset_buttons = []
        i = 0
        max_presets = 10
        for i in range(max_presets):
            preset = presets[i]
            column = floor(i / presets_per_column)
            row = i % presets_per_column
            preset_button = Button(self.frame, text=preset['Name'],
                                   command=lambda id=i: self.preset_click(id))
            preset_button.grid(row=row, column=start_column + column, padx=5, pady=5, sticky="ew")
            self.preset_buttons.append(preset_button)
            i += 1

    def preset_click(self, preset_id):
        self.ovnif.preset_goto(preset_id)

    def preset_add(self, preset_name, preset_id):
        self.ovnif.preset_add(preset_name, preset_id)

    def preset_remove(self, preset_id):
        self.ovnif.preset_remove(preset_id)

    def get_frame(self):
        return self.frame

    def connect_to_camera(self):
        self.ovnif = ONVIFControl(host=self.host, port=self.port, username=self.username, password=self.password)
        self.ovnif.setup()

    def move_left(self, speed):
        if self.enabled:
            self.ovnif.move(-1 * round(speed / 100, 1), 0)

    def move_right(self, speed):
        if self.enabled:
            self.ovnif.move(round(speed / 100, 1), 0)

    def move_up(self, speed):
        if self.enabled:
            self.ovnif.move(0, round(speed / 100, 1))

    def move_down(self, speed):
        if self.enabled:
            self.ovnif.move(0, -1 * round(speed / 100, 1))

    def stop_move(self, speed):
        if self.enabled:
            self.ovnif.stop()

    def zoom_in(self, speed):
        if self.enabled:
            self.ovnif.zoom(round(speed / 100, 1))

    def zoom_out(self, speed):
        if self.enabled:
            self.ovnif.zoom(round(-1 * speed / 100, 1))

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

    def set_message(self, message):
        self.message.configure(text=message)
        self.root.update()
    def close(self):
        pass