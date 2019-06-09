import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as fdialog
from tkinter.scrolledtext import ScrolledText

from typing import Dict, Type, List, Collection, Tuple, Callable

from .TemplateProcessor import *


LARGE_FONT = ("Verdana", 12)


class ButtonSeries (ttk.Frame):
    def __init__(self, parent, controller, button_data: Collection[Tuple[str, Callable[[], None]]], spacing=5, orientation=tk.E):
        super().__init__(parent)
        buttons: List[tk.Button] = list()
        for label, action in button_data:
            buttons.append(ttk.Button(self, text=label, command=action))

        for i, button in enumerate(buttons):
            if orientation == tk.E or orientation == tk.W:
                button.grid(row=0, column=i, padx=spacing, sticky=orientation)
            elif orientation == tk.N or orientation == tk.S:
                button.grid(row=i, column=0, pady=spacing, sticky=orientation)


class FileViewer (ttk.Frame):
    def __init__(self, parent, controller, width, height, default_label,
                 loaded_label=None, editable=True, on_file_loaing=None):
        super().__init__(parent)
        self.default_label = default_label
        self.loaded_label = loaded_label
        self.editable = editable
        self.on_file_loading = on_file_loaing
        self.fname = None
        self.fcontent = None
        self.file_loaded = False
        self.file_viewer = ScrolledText(self, width=width, height=height)
        self.file_viewer_label = ttk.Label(self, text=default_label)
        file_button_data = [("Browse Files...", self.select_and_load_file)]
        if self.editable:
            file_button_data.insert(0, ("Save", self.save_file))

        self.file_buttons = ButtonSeries(self, controller, file_button_data)

        self.file_viewer.config(wrap="word")
        if not self.editable:
            self.file_viewer.config(state="disabled")

        self.file_viewer_label.grid(row=0, column=0, sticky="nw")
        self.file_viewer.grid(row=1, column=0, sticky="nsew")
        self.file_buttons.grid(row=2, column=0, sticky="ne")

    def select_and_load_file(self):
        self.fname = fdialog.askopenfilename(filetypes=(("HTML files", "*.html"), ("XML files", "*.xml")))

        if self.fname:
            with open(self.fname, "r") as h:
                self.fcontent = h.read()

            self.file_viewer.config(state="normal")

            self.file_viewer.delete("1.0", tk.END)

            if self.on_file_loading is None:
                self.file_viewer.insert(tk.END, self.fcontent)
            else:
                self.on_file_loading(self.file_viewer, self.fcontent)

            self.file_viewer_label.config(text=self.fname if self.loaded_label is None else f"{self.loaded_label} ({self.fname.split('/')[-1]})")
            self.file_loaded = True
            if not self.editable:
                self.file_viewer.config(state="disabled")

    def save_file(self):
        if self.file_loaded:
            with open(self.fname, "w") as h:
                h.write(self.file_viewer.get("1.0", tk.END))

        else:
            fdialog.asksaveasfilename()
            self.file_loaded = True
            self.file_viewer_label.config(text=self.fname if self.loaded_label is None else f"{self.loaded_label} ({self.fname.split('/')[-1]})")


class IndexPage (ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.input_template = FileViewer(self, controller, 60, 20, "No input template selected", "Input template")
        self.output_template = FileViewer(self, controller, 60, 20, "No output template selected", "Output template")
        self.document = FileViewer(self, controller, 60, 45, "No file selected", editable=False)
        buttons = [
            ("Check", self.highlight_matches),
            ("Preview Changes...", self.confirm_changes)
        ]
        self.buttons = ButtonSeries(self, controller, buttons)

        self.input_template.grid(column=0, row=0, padx=10, pady=10, sticky="ns")
        self.output_template.grid(column=0, row=1, padx=10, pady=10, sticky="sn")
        self.document.grid(column=1, row=0, rowspan=2, padx=10, pady=10, sticky="n")
        self.buttons.grid(row=2, column=0, columnspan=2, sticky="e", padx=10, pady=10)

    def confirm_changes(self):
        if self.document.fcontent is None or self.document.fcontent == "" \
                or self.input_template.fcontent is None or self.input_template.fcontent == "" \
                or self.output_template.fcontent is None or self.output_template.fcontent == "":
            return

        ConfirmChangesDialog(self, self.controller, self.input_template.fname, self.output_template.fname,
                             self.document.fname, self.document.fcontent)

    def highlight_matches(self):
        reify = TemplateProcessor(self.input_template.file_viewer.get("1.0", tk.END),
                                  self.output_template.file_viewer.get("1.0", tk.END),
                                  True)

        matches = reify.find(self.document.fname)



class ConfirmChangesDialog (tk.Toplevel):
    def __init__(self, parent, controller, input_template, output_template, file, orig_contents):
        super().__init__()
        self.wm_title("Confirm Replacements")
        self.orig_label = ttk.Label(self, text="Original")
        self.new_label = ttk.Label(self, text="After Changes")
        self.orig_document = ScrolledText(self, width=60, height=30)
        self.new_document = ScrolledText(self, width=60, height=30)
        self.reify = TemplateProcessor(input_template, output_template, False)
        button_data = [
            ("Cancel", self.destroy),
            ("Confirm", lambda: self.reify.find_and_replace(file, True)),
            ("Save As...", self.save_changes_as)
        ]
        self.buttons = ButtonSeries(self, controller, button_data)

        self.orig_document.insert(tk.END, orig_contents)
        self.new_document.insert(tk.END, self.reify.find_and_replace(file, False))

        self.orig_document.config(state="disabled")

        self.orig_label.grid(row=0, column=0, padx=10, sticky="nw")
        self.orig_document.grid(row=1, column=0, padx=10, sticky="nse")
        self.new_label.grid(row=0, column=1, padx=10, sticky="nw")
        self.new_document.grid(row=1, column=1, padx=10, sticky="nsw")
        self.buttons.grid(row=2, column=1, padx=10, pady=10, sticky="se")

    def save_changes_as(self):
        filename = fdialog.asksaveasfilename()
        if filename:
            with open(filename, "w") as h:
                h.write(self.new_document.get("1.0", tk.END))

            self.destroy()


class ReifyOptionsMenu (tk.Menu):
    def __init__(self, parent):
        super().__init__()

        self.file_menu = tk.Menu(self)
        self.file_menu.add_command(label="Open", command=lambda: None)
        self.file_menu.add_command(label="Save All", command=lambda: None)
        self.file_menu.add_command(label="Save As...", command=lambda: None)
        self.file_menu.add_command(label="Close", command=lambda: None)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Quit Reify", command=lambda: None)

        self.edit_menu = tk.Menu(self)
        self.edit_menu.add_command(label="Undo", command=lambda: None)
        self.edit_menu.add_command(label="Redo", command=lambda: None)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Cut", command=lambda: None)
        self.edit_menu.add_command(label="Copy", command=lambda: None)
        self.edit_menu.add_command(label="Paste", command=lambda: None)
        self.edit_menu.add_command(label="Select All", command=lambda: None)

        self.add_cascade(menu=self.file_menu, label="File")
        self.add_cascade(menu=self.edit_menu, label="Edit")


class ReifyGUI (tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__()

        self.wm_title("Reify")
        self.option_add("*tearOff", tk.FALSE)
        self.menu_bar = ReifyOptionsMenu(self)
        self["menu"] = self.menu_bar

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames: Dict[Type[tk.Frame], tk.Frame] = dict()
        # self.tabs = ttk.Notebook(self)
        # self.tabs.add(IndexPage(container, self), text="Untitled")
        # self.tabs.select()

        for Page in (IndexPage,):
            page = Page(container, self)
            self.frames[Page] = page
            page.grid(row=0, column=0, sticky="nsew")

        self.show_frame(IndexPage)

    def show_frame(self, controller: Type[tk.Frame]):
        frame = self.frames[controller]
        frame.tkraise()

    def show_tab(self, controller: Type[tk.Frame]):
        pass


if __name__ == "__main__":
    app = ReifyGUI()
    app.mainloop()
