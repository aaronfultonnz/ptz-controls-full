import os
from lib.pyinstaller_helper import resource_path
from tkinter import Button, PhotoImage, Label, Toplevel, Entry, Frame, END
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
        self.selected_preset_idx = -1
        self.presets = []
        self.preset_edit_buttons = []

        self.preset_save_image = PhotoImage(file=resource_path(os.path.join('assets', 'save.png')))
        self.preset_edit_image = PhotoImage(file=resource_path(os.path.join('assets', 'edit.png')))

        text = """Camera Controller can use 10 presets.
To change a preset click the edit button
then enter a new name. Clicking save will
save the preset at the current camera location."""
        self.intro = Label(self, text=text, background="white", anchor="w", justify="left")
        self.intro.grid(row=0, column=0, padx=0.1, pady=0.1, sticky='W')

        self.add_frame = Frame(self, background='white')
        self.add_frame.grid(row=1, column=0, padx=0.1, pady=0.1, sticky='W')

        vcmd = (self.register(self.name_validate), '%P')
        self.name = Entry(self.add_frame, background='white', validate="key", validatecommand=vcmd, width=35)
        self.name.grid(row=0, column=0, padx=5, pady=5)
        self.save_button = Button(self.add_frame, text="Save", image=self.preset_save_image, height=20,
                                  width=20,
                                  background='white', border=0, command=self.save, state='disabled')
        self.save_button.grid(row=0,column=1, padx=5, pady=5)

        if not self.camera.enabled:
            self.name.configure(state='disabled')

        self.reload()

    def name_validate(self, P):
        if P == '':
            self.save_button.configure(state='disabled')
        else:
            self.save_button.configure(state='normal')

        return True

    def reload(self):
        try:
            if self.camera.enabled is False:
                raise Exception("Camera not started")

            self.presets = self.camera.ovnif.preset_list()
            if self.preset_frame:
                self.preset_frame.destroy()
                self.preset_labels = []
                self.preset_edit_buttons = []

            self.preset_frame = Frame(self, background='white')
            self.preset_frame.grid(row=2, column=0, padx=0.1, pady=0.1, sticky='W')
            start_row_offset = 2
            max_presets = 10
            for idx in range(max_presets):
                row = idx + start_row_offset
                name = self.presets[idx]['Name'] if idx <= len(self.presets) else f"Preset {idx + 1}"

                preset_edit_button = Button(self.preset_frame, image=self.preset_edit_image, height=20,
                                            width=20,
                                            background='white', border=0,
                                            command=lambda idx=idx: self.edit(idx))
                preset_edit_button.grid(row=row, column=0, padx=0, pady=0)

                preset_label = Label(self.preset_frame, text=name, background="white", anchor="w", width=15)
                preset_label.grid(row=row, column=1, padx=0, pady=0, sticky="w")

                self.preset_labels.append(preset_label)
                self.preset_edit_buttons.append(preset_edit_button)

        except Exception:
            self.set_message('Camera not started')

    def edit(self, idx):
        self.selected_preset_idx = idx
        name = self.presets[idx]['Name'] if idx <= len(self.presets) else f"Preset {idx + 1}"
        self.name.delete(0, END)
        self.name.insert(0, name)

    def save(self):
        try:
            name = self.name.get()
            token = self.presets[self.selected_preset_idx]['token'] if self.selected_preset_idx <= len(self.presets) else f""
            self.camera.preset_add(name, token)
            self.reload()
        except ONVIFError as err:
            self.set_message(f"Error adding preset: {err}")

    def set_message(self, message):
        self.message.configure(text=message)
        self.update()

    def close(self):
        self.close_cb()
        self.destroy()
