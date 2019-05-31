import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as fdialog
from tkinter.scrolledtext import ScrolledText

from typing import Dict, Type

from .TemplateProcessor import *


LARGE_FONT = ("Verdana", 12)


class FileViewer (tk.Frame):
    def __init__(self, parent, controller, width, height, default_label,
                 loaded_label=None, editable=True, on_file_loaing=None):
        super().__init__(parent)
        self.default_label = default_label
        self.loaded_label = loaded_label
        self.editable = editable
        self.on_file_loading = on_file_loaing
        self.file_viewer = ScrolledText(self, width=width, height=height)
        self.file_viewer_label = ttk.Label(self, text=default_label)
        self.file_select_button = ttk.Button(self, text="Browse Files...", command=self.select_and_load_file)

        self.file_viewer.config(wrap="word")
        if not self.editable:
            self.file_viewer.config(state="disabled")

        self.file_viewer_label.grid(row=0, column=0, sticky="w")
        self.file_select_button.grid(row=0, column=1, sticky="e")
        self.file_viewer.grid(row=2, column=0, columnspan=2, sticky="nsew")

    def select_and_load_file(self):
        fname = fdialog.askopenfilename(filetypes=(("HTML files", "*.html"), ("XML files", "*.xml")))

        if fname:
            with open(fname, "r") as h:
                fcontent = h.read()

            self.file_viewer.config(state="normal")

            self.file_viewer.delete("1.0", tk.END)

            if self.on_file_loading is None:
                self.file_viewer.insert(tk.END, fcontent)
            else:
                self.on_file_loading(self.file_viewer, fcontent)

            self.file_viewer_label.config(text=fname if self.loaded_label is None else f"{self.loaded_label} ({fname.split('/')[-1]})")

            if not self.editable:
                self.file_viewer.config(state="disabled")


class IndexPage (tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        input_template = FileViewer(self, controller, 60, 20, "No input template selected", "Input template")
        output_template = FileViewer(self, controller, 60, 20, "No output template selected", "Output template")
        document = FileViewer(self, controller, 60, 43, "No file selected", editable=False)
        preview_button = ttk.Button(self, text="Preview Changes...")

        input_template.grid(column=0, row=0, padx=10, pady=10, sticky="ns")
        output_template.grid(column=0, row=1, padx=10, pady=10, sticky="sn")
        document.grid(column=1, row=0, rowspan=2, padx=10, pady=10, sticky="n")
        preview_button.grid(row=2, column=0, columnspan=2, sticky="e", padx=10, pady=10)


class ReifyGUI (tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__()

        self.wm_title("Reify")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames: Dict[Type[tk.Frame], tk.Frame] = dict()

        for Page in (IndexPage,):
            page = Page(container, self)
            self.frames[Page] = page
            page.grid(row=0, column=0, sticky="nsew")

        self.show_frame(IndexPage)

    def show_frame(self, controller: Type[tk.Frame]):
        frame = self.frames[controller]
        frame.tkraise()


if __name__ == "__main__":
    app = ReifyGUI()
    app.mainloop()
