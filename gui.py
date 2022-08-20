import sys
import os
from tkinter import Tk, Button, Frame, filedialog, Label
from tkinter import ttk
import tkinter
from tkinter.scrolledtext import ScrolledText
import img_to_video as converter
import threading

class StdoutRedirector(object):

    # Pass reference to the text widget
    def __init__(self, text_widget):
        self.text_space = text_widget

    # Write text and scroll to end
    def write(self,string):
        self.text_space.insert('end', string)
        self.text_space.see('end')

        # force refresh of the widget to be sure that thing are displayed
        # self.text_space.update_idletasks()
        
    # Needed for file like object
    def flush(self):
        pass

class Observer(object):

    def __init__(self, main_gui):
        self.gui = main_gui

    # Updated how many images were processed since previous call of
    # update().
    def update(self, value):
        pass

    # Notify that the processing is complete
    def done(self):
        print("Done!")
        self.gui.enable()

    # Set max number of image to process
    def set_max(self, max_value):
        pass
        #self.max_val = max_value

# TODO: Destroy the thread if it's closed
class MainGUI(Frame):

    def __init__(self, root=None):
        self.create_widgets(root)

        self.observer = Observer(self)

    def create_widgets(self, root):
        self.frm = ttk.Frame(root, padding = 10)
        self.frm.grid()
        
        # self.frm.columnconfigure(0, weight=1)
        self.frm.columnconfigure(1, weight=1)
        
        folder_button = ttk.Button(self.frm, text="Fodler...", command=self.select_folder)
        folder_button.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        self.folder_label = ttk.Label(self.frm, text="/Users/andlev/Workspace/ImageDropletsToVideo/1min")
        self.folder_label.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        total_image_width = ttk.Label(self.frm, text="Image width, mm:")
        total_image_width.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.image_width_entry = ttk.Entry(self.frm)
        self.image_width_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        capture_interval_label = ttk.Label(self.frm, text="Capture interval, s:")
        capture_interval_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.capture_interval_entry = ttk.Entry(self.frm)
        self.capture_interval_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        video_time_label = ttk.Label(self.frm, text="Video time (approx.), s:")
        video_time_label.grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.video_time_entry = ttk.Entry(self.frm)
        self.video_time_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        self.generate_button = ttk.Button(self.frm, text="Generate", command=self.start_generation_in_thread)
        self.generate_button.grid(row=5, column=1, sticky="e")
        
        self.log_widget = ScrolledText(self.frm, font=("consolas", "12", "normal"))
        self.log_widget.grid(row=6, column=0, columnspan=2, sticky="nsew")
        sys.stdout = StdoutRedirector(self.log_widget)
        sys.stderr = sys.stdout

    def enable(self):
        self.generate_button["state"] = "normal"
        
    def select_folder(self):
        directory = filedialog.askdirectory(initialdir = "./")
        self.folder_label.configure(text = directory)

    def reset_logging(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def start_generation_in_thread(self):
        self.generate_button["state"] = "disabled"
        threaded = threading.Thread(target=self.start_generation)
        threaded.start()

    def start_generation(self):
        folder_path = self.folder_label.cget("text")
        #image_width_mm = float(self.image_width_entry.get())
        #capture_interval_s = int(self.capture_interval_entry.get())
        video_time_s = int(self.video_time_entry.get())

        image_width_mm = 4.7
        capture_interval_s = 10
        
        converter.generate_img_to_video(folder_path,
                                        image_width_mm,
                                        capture_interval_s,
                                        video_time_s,
                                        self.observer)
        
if __name__ == "__main__":
    root = Tk();
    root.wm_title("Images to Video conversion")
    app = MainGUI(root)
    root.resizable(False, False)
    root.mainloop()

