import os
from lib.pyinstaller_helper import resource_path
from tkinter import Button, PhotoImage, Label, Toplevel, Entry, Frame
from onvif.exceptions import ONVIFError


class ManagePresets(Toplevel):
    def __init__(self, master, camera, close_cb):
        super().__init__(master=master)
        self.camera = camera
        self.close_cb = close_cb

        self.title("Presets")
        self.configure(background='white')
        self.iconbitmap(resource_path(os.path.join('assets', 'favicon.ico')))
        self.protocol("WM_DELETE_WINDOW", self.close)

        self.message = Label(self, text="", anchor="center", background="white")
        self.message.grid(row=0, column=0)

        self.preset_frame = None
        self.preset_labels = []
        self.preset_delete_buttons = []
        self.preset_hide_buttons = []
        self.state = []
        self.preset_delete_image = PhotoImage(file=resource_path(os.path.join('assets', 'trash.png')))
        self.preset_hidden_image = PhotoImage(file=resource_path(os.path.join('assets', 'hidden.png')))
        self.preset_visible_image = PhotoImage(file=resource_path(os.path.join('assets', 'visible.png')))

        self.add_frame = Frame(self, background='white')
        self.add_frame.grid(row=1, column=0, padx=0.1, pady=0.1)

        vcmd = (self.register(self.name_validate), '%P')
        self.name = Entry(self.add_frame, background='white', validate="key", validatecommand=vcmd)
        self.name.grid(row=0, column=0, padx=5, pady=5)
        self.add_button = Button(self.add_frame, text="Add", background='white', command=self.add, state='disabled')
        self.add_button.grid(row=0, column=1, padx=5, pady=5)

        if not self.camera.enabled:
            self.name.configure(state='disabled')

        self.reload()

    def name_validate(self, P):
        if P == '':
            self.add_button.configure(state='disabled')
        else:
            self.add_button.configure(state='normal')

        return True

    def reload(self):
        try:
            if not self.camera.enabled:
                raise Exception("Camera not started")

            presets = self.camera.camera.preset_list()
            if self.preset_frame:
                self.preset_frame.destroy()
                self.preset_labels = []
                self.preset_delete_buttons = []
                self.preset_hide_buttons = []

            self.state = [True] * len(presets)
            self.preset_frame = Frame(self, background='white')
            self.preset_frame.grid(row=1, column=0, padx=0.1, pady=0.1)
            start_row_offset = 2
            for idx, preset in enumerate(presets):
                row = idx + start_row_offset
                preset_delete_button = Button(self.preset_frame, image=self.preset_delete_image, height=20, width=20,
                                              background='white', border=0, command=lambda idx=idx: self.delete(idx))
                preset_delete_button.grid(row=row, column=0, padx=0, pady=0)

                preset_hide_button = Button(self.preset_frame, image=self.preset_visible_image, height=20, width=20,
                                            background='white', border=0,
                                            command=lambda idx=idx: self.toggle_visibility(idx))
                if preset['name'] in self.camera.hidden_presets:
                    preset_hide_button.configure(image=self.preset_hidden_image)
                    self.state[idx] = False

                preset_hide_button.grid(row=row, column=1, padx=0, pady=0)

                preset_label = Label(self.preset_frame, text=preset['name'], background="white", anchor="w", width=15)
                preset_label.grid(row=row, column=2, padx=0, pady=0, sticky="w")

                self.preset_labels.append(preset_label)
                self.preset_delete_buttons.append(preset_delete_button)
                self.preset_hide_buttons.append(preset_hide_button)
        except Exception:
            self.set_message('Camera not started')

    def toggle_visibility(self, idx):
        if self.state[idx] is True:
            self.preset_hide_buttons[idx].configure(image=self.preset_hidden_image)
        else:
            self.preset_hide_buttons[idx].configure(image=self.preset_visible_image)

        self.state[idx] = True if self.state[idx] is False else False

    def add(self):
        try:
            name = self.name.get()
            self.camera.preset_add(name)
            self.reload()
        except ONVIFError as err:
            self.set_message(f"Error adding preset: {err}")

    def delete(self, idx):
        try:
            self.camera.preset_remove(idx)
            self.reload()
        except ONVIFError as err:
            self.set_message(f"Error adding preset: {err}")

    def set_message(self, message):
        self.message.configure(text=message)
        self.update()

    def close(self):
        hidden = []
        for idx, val in enumerate(self.state):
            if val is False:
                hidden.append(self.preset_labels[idx].cget('text'))
        self.close_cb(self.camera.name, hidden)
        self.destroy()
