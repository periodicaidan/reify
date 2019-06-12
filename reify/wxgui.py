import wx
import wx.aui as aui
from typing import *

from .TemplateProcessor import TemplateProcessor


ButtonData = NewType("ButtonData", Tuple[str, Callable[[wx.Event], None]])


class ButtonSeries (wx.Panel):
    def __init__(self, parent: wx.Window,
                 button_data: Collection[ButtonData],
                 padding: int = 10,
                 orientation: int = wx.HORIZONTAL):
        super().__init__(parent)
        sizer = wx.BoxSizer(orientation)

        for i, (label, callback) in enumerate(button_data):
            btn = wx.Button(self, id=wx.ID_ANY, label=label)
            btn.Bind(wx.EVT_BUTTON, callback)
            if i == 0:
                sizer.Add(btn)
            elif orientation == wx.HORIZONTAL:
                sizer.Add(btn, flag=wx.LEFT, border=padding)
            elif orientation == wx.VERTICAL:
                sizer.Add(btn, flag=wx.TOP, border=padding)

        self.SetSizer(sizer)


class FileViewerContextMenu (wx.Menu):
    def __init__(self, parent: "FileViewer"):
        super().__init__()
        self.parent = parent
        save_item = wx.MenuItem(self, wx.ID_ANY, "Save Changes")
        open_item = wx.MenuItem(self, wx.ID_ANY, "Open File")
        add_to_proj = wx.MenuItem(self, wx.ID_ANY, "Add to Project")
        clear_item = wx.MenuItem(self, wx.ID_ANY, "Clear")

        self.Append(save_item)
        self.Append(open_item)
        self.Append(add_to_proj)
        self.AppendSeparator()
        self.Append(clear_item)

        self.Bind(wx.EVT_MENU, self.parent.save_file, save_item)
        self.Bind(wx.EVT_MENU, self.parent.select_and_load_file, open_item)
        self.Bind(wx.EVT_MENU, lambda e: self.parent.file_viewer.Clear(), clear_item)


class FileViewer (wx.Panel):
    def __init__(self, parent: wx.Window, name: str, default_label=None, readonly: bool = False):
        super().__init__(parent)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.readonly = readonly
        self.filename = None
        self.name = name
        ro_mask = 0b11111111 if readonly else 0

        self.file_viewer_label = wx.StaticText(self, label=default_label or f"No {name} Selected")
        self.file_viewer = wx.TextCtrl(self, style=wx.TE_MULTILINE | (wx.TE_READONLY & ro_mask))
        default_style = wx.TextAttr()
        default_style.SetFontFamily(wx.FONTFAMILY_MODERN)
        self.file_viewer.SetDefaultStyle(default_style)
        file_button_data: List[ButtonData] = [
            ("Browse...", self.select_and_load_file)
        ]

        if not readonly:
            file_button_data.insert(0, ("Save", self.save_file))

        self.file_buttons = ButtonSeries(self, file_button_data)

        self.sizer.Add(self.file_viewer_label, flag=wx.EXPAND | wx.ALL, border=10)
        self.sizer.Add(self.file_viewer, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)
        self.sizer.Add(self.file_buttons, flag=wx.ALIGN_RIGHT | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

        self.SetSizer(self.sizer)

        self.file_viewer.Bind(wx.EVT_RIGHT_DOWN, lambda e: self.PopupMenu(FileViewerContextMenu(self), e.GetPosition()))

    def open_file(self, pathname: Optional[str]):
        if pathname is None:
            return
        try:
            with open(pathname, "r") as h:
                self.file_viewer.SetValue(h.read())
                self.filename = pathname
                self.file_viewer_label.SetLabel(pathname)
        except IOError:
            wx.LogError(f"Cannot open file {pathname}")

    def select_and_load_file(self, e: wx.Event) -> None:
        with wx.FileDialog(self, message="Select file",
                           wildcard="HTML Files (*.html;*.htm)|*.html;*.htm|"
                                          "XML Files (*.xml)|*.xml|"
                                          "All files|*.*",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fd:

            if fd.ShowModal() == wx.ID_CANCEL:
                return

            pathname = fd.GetPath()
            self.open_file(pathname)

    def save_file(self, e: wx.Event) -> None:
        if self.filename is None:
            with wx.FileDialog(self, message=f"Save {self.name.lower()} as new file",
                                name=f"Save {self.name.lower()} as new file",
                               wildcard="HTML Files (*.html;*.htm)|*.html;*.htm|"
                                        "XML Files (*.xml)|*.xml|"
                                        "All files|*.*",
                               style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fd:

                if fd.ShowModal() == wx.ID_CANCEL:
                    return

                pathname = fd.GetPath()
                self.filename = pathname

        self.file_viewer.SaveFile(self.filename)


class ReifyMenuBar (wx.MenuBar):
    def __init__(self, parent: wx.Window, notebook: wx.Notebook, style=0):
        super().__init__(style)
        self.parent = parent
        self.notebook = notebook
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.set_page)
        self.current_page: "IndexPanel" = notebook.GetPage(notebook.GetSelection())

        file_menu = wx.Menu()
        self.new_item = file_menu.Append(wx.ID_NEW, "&New", "Start a new Reify project")
        self.open_item = file_menu.Append(wx.ID_OPEN, "&Open", "Open a Reify project")
        self.save_item = file_menu.Append(wx.ID_SAVE, "&Save", "Save Reify project")
        self.save_as_item = file_menu.Append(wx.ID_SAVEAS, "Save &As...\tCtrl+Shift+S",
                                        "Save this Reify project to a new file")
        file_menu.AppendSeparator()
        self.close_item = file_menu.Append(wx.ID_CLOSE, "&Close", "Close Project")
        self.quit_item = file_menu.Append(wx.ID_EXIT, "&Quit", "Exit Reify")

        self.Bind(wx.EVT_MENU, self.current_page.open_reproj, self.open_item)
        self.Bind(wx.EVT_MENU, self.current_page.save_all, self.save_item)
        self.Bind(wx.EVT_MENU, self.current_page.save_as, self.save_as_item)
        self.Bind(wx.EVT_MENU, self.close_reproj, self.close_item)
        self.Bind(wx.EVT_MENU, lambda e: self.parent.Close(), self.quit_item)

        edit_menu = wx.Menu()
        edit_menu.Append(wx.ID_UNDO, "&Undo")
        edit_menu.Append(wx.ID_REDO, "&Redo")
        edit_menu.AppendSeparator()
        edit_menu.Append(wx.ID_CUT, "&Cut")
        edit_menu.Append(wx.ID_COPY, "&Copy")
        edit_menu.Append(wx.ID_PASTE, "&Paste")
        edit_menu.Append(wx.ID_DELETE, "&Delete")

        self.Append(file_menu, "&File")
        self.Append(edit_menu, "&Edit")

    def close_reproj(self, e: wx.Event):
        idx = self.notebook.GetSelection()
        self.notebook.RemovePage(idx)
        self.notebook.SetSelection(idx - 1)

    def set_page(self, e: wx.BookCtrlEvent):
        idx = e.GetSelection()
        self.Unbind(wx.EVT_MENU, self.open_item)
        self.Unbind(wx.EVT_MENU, self.save_item)
        self.Unbind(wx.EVT_MENU, self.save_as_item)

        self.current_page = self.notebook.GetPage(idx)
        self.Bind(wx.EVT_MENU, self.current_page.open_reproj, self.open_item)
        self.Bind(wx.EVT_MENU, self.current_page.save_all, self.save_item)
        self.Bind(wx.EVT_MENU, self.current_page.save_as, self.save_as_item)

        e.Skip()


class ConfirmChangesDialog (wx.Dialog):
    def __init__(self, input_template: str, output_template: str, document: FileViewer, *args, **kw):
        super().__init__(title="Confirm Replacements", *args, **kw)
        self.SetSize(800, 500)

        self.root = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.document = document
        self.input_template = input_template
        self.output_template = output_template
        self.file_contents = document.file_viewer.GetValue()
        self.reify = TemplateProcessor(input_template, output_template, False)

        self.orig_label = wx.StaticText(self, label="Original")
        self.new_label = wx.StaticText(self, label="After Changes")
        self.orig_document = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.new_document = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        default_style = wx.TextAttr()
        default_style.SetFontFamily(wx.FONTFAMILY_MODERN)
        self.orig_document.SetDefaultStyle(default_style)
        self.orig_document.SetValue(self.file_contents)
        self.new_document.SetDefaultStyle(default_style)
        self.new_document.SetValue(self.reify.find_and_replace(document.filename, False))
        button_data: List[ButtonData] = [
            ("Cancel", lambda e: self.Destroy()),
            ("Confirm", lambda e: self.reify.find_and_replace(document.filename, True)),
            ("Save As...", self.save_changes_as)
        ]
        self.buttons = ButtonSeries(self, button_data)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        vbox1 = wx.BoxSizer(wx.VERTICAL)
        vbox1.Add(self.orig_label, flag=wx.ALL, border=10)
        vbox1.Add(self.orig_document, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, proportion=1, border=10)
        hbox1.Add(vbox1, flag=wx.EXPAND, proportion=1)

        vbox2 = wx.BoxSizer(wx.VERTICAL)
        vbox2.Add(self.new_label, flag=wx.ALL, border=10)
        vbox2.Add(self.new_document, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, proportion=1, border=10)
        hbox1.Add(vbox2, flag=wx.EXPAND, proportion=1)

        sizer.Add(hbox1, flag=wx.EXPAND, proportion=1)

        sizer.Add(self.buttons, flag=wx.ALIGN_RIGHT | wx.ALL, border=10)

        self.SetSizer(sizer)

    def save_changes_as(self, e: wx.Event) -> None:
        filename: str = wx.FileSelector("Select a File to Save To", flags=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if filename.strip():
            self.new_document.SaveFile(filename)
            self.Destroy()
        else:
            return


class IndexPanel (wx.Panel):
    def __init__(self, parent: wx.Notebook):
        super().__init__(parent)

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.parent = parent
        self.input_template_viewer = FileViewer(self, "Input Template")
        self.output_template_viewer = FileViewer(self, "Output Template")
        self.document_viewer = FileViewer(self, "Document", readonly=True)
        self.reproj: Dict[str, Optional[str]] = {
            "project_path": None,
            "input_template": None,
            "output_template": None,
            "document": None
        }

        button_data: List[ButtonData] = [
            ("Check", lambda e: self.highlight_matches()),
            ("Preview Changes...", self.confirm_changes)
        ]
        self.buttons = ButtonSeries(self, button_data)

        file_viewer_grid = wx.BoxSizer(wx.HORIZONTAL)
        template_viewer_sizer = wx.BoxSizer(wx.VERTICAL)
        template_viewer_sizer.Add(self.input_template_viewer, flag=wx.EXPAND, proportion=1)
        template_viewer_sizer.Add(self.output_template_viewer, flag=wx.EXPAND, proportion=1)
        file_viewer_grid.Add(template_viewer_sizer, flag=wx.EXPAND, proportion=1)
        file_viewer_grid.Add(self.document_viewer, flag=wx.EXPAND, proportion=1)

        sizer.Add(file_viewer_grid, flag=wx.EXPAND, proportion=1)
        sizer.Add(self.buttons, flag=wx.ALIGN_RIGHT | wx.ALL, border=10)

        self.SetSizer(sizer)

    def open_reproj(self, e: wx.Event):
        with wx.FileDialog(self, "Select Project", wildcard="Reify Project Files(*.reproj)|*.reproj",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fd:

            if fd.ShowModal() == wx.ID_CANCEL:
                return

            project_path: str = fd.GetPath()
            with open(project_path, "r") as h:
                self.reproj.update(**{
                    "project_path": project_path,
                    "input_template": h.readline().strip(),
                    "output_template": h.readline().strip(),
                    "document": h.readline().strip()
                })

                for k, v in self.reproj.items():
                    if v == "":
                        self.reproj[k] = None

                self.input_template_viewer.open_file(self.reproj["input_template"])
                self.output_template_viewer.open_file(self.reproj["output_template"])
                self.document_viewer.open_file(self.reproj["document"])

                e.Skip()

    def save_as(self, e: wx.Event):
        self.save_all(e)

        with wx.FileDialog(self, "Save as New Reify Project", defaultFile="untitled.reproj",
                           wildcard="Reify Project Files (*.reproj)|*.reproj",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fd:

            if fd.ShowModal() == wx.ID_CANCEL:
                return

            self.reproj["project_path"] = fd.GetPath()

            with open(self.reproj["project_path"], "w") as h:
                h.writelines([
                    self.reproj["input_template"],
                    self.reproj["output_template"],
                    self.reproj["document"]
                ])

    def save_all(self, e: wx.Event):
        self.input_template_viewer.save_file(e)
        self.output_template_viewer.save_file(e)
        self.document_viewer.save_file(e)
        print("Saved")

    def confirm_changes(self, e: wx.Event) -> None:
        if self.input_template_viewer.filename is None \
                or self.output_template_viewer.filename is None \
                or self.document_viewer.filename is None:
            error_string = "Could not perform find-and-replace due to the following errors:\n\n"
            for file_viewer in (self.input_template_viewer, self.output_template_viewer, self.document_viewer):
                if file_viewer.filename is None:
                    error_string += f"No {file_viewer.name.lower()} selected\n"
            wx.MessageBox(error_string, "Error", style=wx.OK | wx.ICON_ERROR)
            return

        with ConfirmChangesDialog(parent=self,
                                  input_template=self.input_template_viewer.file_viewer.GetValue(),
                                  output_template=self.output_template_viewer.file_viewer.GetValue(),
                                  document=self.document_viewer) as ccd:
            ccd.ShowModal()

    def highlight_matches(self):
        text = self.document_viewer.file_viewer
        text.SetStyle(1, len(text.GetValue()), text.GetDefaultStyle())
        reify = TemplateProcessor(
            self.input_template_viewer.file_viewer.GetValue(),
            self.output_template_viewer.file_viewer.GetValue(),
            False
        )
        matches: Tuple[Match] = tuple(reify.find(self.document_viewer.filename))
        if len(matches) == 0:
            return

        highlight = wx.TextAttr(wx.BLACK, wx.GREEN)
        highlight.SetFontWeight(wx.FONTWEIGHT_BOLD)
        for i, m in enumerate(matches):
            for j in range(len(m.groups())):
                text.SetStyle(m.start(j + 1), m.end(j + 1), highlight)


class IndexPage (wx.Frame):
    def __init__(self, open_files, *args, **kwargs):
        super().__init__(parent=None, title="Reify")
        self.proj = None
        self.open_files = open_files
        self.SetSize(1000, 1000)
        self.SetMinSize(wx.Size(500, 500))
        self.notebook = wx.Notebook(self)
        self.panel = IndexPanel(self.notebook)
        self.panel.SetFocus()

        self.notebook.AddPage(self.panel, "untitled")
        self.add_page()
        self.notebook.AddPage(wx.Panel(self.notebook), "+")

        menubar = ReifyMenuBar(self, self.notebook)
        self.SetMenuBar(menubar)
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.change_or_add_page)

        self.Show()

    def change_or_add_page(self, e: wx.BookCtrlEvent):
        idx = e.GetSelection()
        print(idx)
        if idx == self.notebook.GetPageCount() - 1:
            self.add_page()
        self.notebook.SetSelection(idx)

        e.Skip()

    def add_page(self):
        self.notebook.InsertPage(self.notebook.GetPageCount() - 1, IndexPanel(self.notebook), "untitled")

    def open_reproj(self):
        with wx.FileDialog(self, "Select Project", wildcard="Reify Project Files(*.reproj)|*.reproj",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fd:

            if fd.ShowModal() == wx.ID_CANCEL:
                return

            pathname = fd.GetPath()
            with open(pathname, "r") as h:
                self.proj = pathname
                self.open_files["input_template"] = h.readline().strip()
                self.open_files["output_template"] = h.readline().strip()
                self.open_files["document"] = h.readline().strip()

                self.panel.input_template_viewer.open_file(self.open_files["input_template"])
                self.panel.output_template_viewer.open_file(self.open_files["output_template"])
                self.panel.document_viewer.open_file(self.open_files["document"])

                self.notebook.SetPageText(self.notebook.GetSelection(), self.proj.split("/")[-1])

    def save_reproj(self, e: wx.Event):
        if self.proj is None:
            pass

        self.panel.save_all(e)
        with open(self.proj, "w") as h:
            h.writelines([
                self.open_files["input_template"],
                self.open_files["output_template"],
                self.open_files["document"]
            ])


class ReifyGUI (wx.App):
    def __init__(self, redirect=False, filename=None, useBestVisual=False, clearSigInt=True):
        super().__init__(redirect, filename, useBestVisual, clearSigInt)
        self.SetAppName("Reify")
        self.SetAppDisplayName("Reify")
        self.open_files = {"input_template": None, "output_template": None, "document": None}

    def mainloop(self):
        frame = IndexPage(self.open_files)
        self.MainLoop()
