# Import required Libraries
from tkinter import *
from PIL import Image, ImageTk
import cv2

# Create an instance of TKinter Window or frame
win = Tk()

# Set the size of the window
win.geometry("700x350")  # Create a Label to capture the Video frames
label = Label(win)
label.grid(row=0, column=0)
cap = cv2.VideoCapture("rtsp://demo:demo@ipvmdemo.dyndns.org:5541/onvif-media/media.amp?profile=profile_1_h264&sessiontimeout=60&streamtype=unicast")


# Define function to show frame
preview_height=200
preview_fps = 20
def show_frames():
    cv2image = cv2.cvtColor(cap.read()[1], cv2.COLOR_BGR2RGB)
    ratio = cv2image.shape[0] / cv2image.shape[1]
    width = int(preview_height/ratio)
    resized = cv2.resize(cv2image, (width, preview_height), interpolation=cv2.INTER_AREA)
    img = Image.fromarray(resized)
    imgtk = ImageTk.PhotoImage(image=img)
    label.imgtk = imgtk
    label.configure(image=imgtk)
    speed = int(1000/preview_fps)
    label.after(speed, show_frames)

show_frames()
win.mainloop()