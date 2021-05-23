from TextEditorModel import TextEditorModel
from TextEditorModel import Location
from TextEditorModel import LocationRange
from ClipboardStack import ClipboardStack
from tkinter.filedialog import askopenfile
from tkinter.filedialog import asksaveasfile
from importlib import import_module
import tkinter as tk
import tkinter.font as tkf
import os
import sys


class TextEditor(tk.Tk):

    def __init__(self, text_model):
        tk.Tk.__init__(self)
        self.text_model = text_model
        self.opened_file = None
        self.clipboard = ClipboardStack()
        self.indent_length = 3
        self.font = tkf.nametofont("TkHeadingFont")
        self.cursor = None
        self.text_model.add_cursor_observer(self)
        self.text_model.add_text_observer(self)
        self.clipboard.add_clipboard_observer(self)
        self.text_model.undo_manager.add_undo_stack_observer(self)
        self.text_model.undo_manager.add_redo_stack_observer(self)
        self.text_model.add_selection_observer(self)
        self.title("Text Editor")
        self.option_add('*tearOff', False)
        self.menu_bar = tk.Menu(self)
        self.file_menu = tk.Menu()
        self.file_menu.add_command(label="Open", command=self.open_command)
        self.file_menu.add_command(label="Save", command=self.save_command)
        self.file_menu.add_command(label="Exit", command=self.exit_command)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.edit_menu = tk.Menu()
        self.edit_menu.add_command(label="Undo", command=self.undo_command, state="disabled")
        self.edit_menu.add_command(label="Redo", command=self.redo_command, state="disabled")
        self.edit_menu.add_command(label="Cut", command=self.cut_command, state="disabled")
        self.edit_menu.add_command(label="Copy", command=self.copy_command, state="disabled")
        self.edit_menu.add_command(label="Paste", command=self.paste_command, state="disabled")
        self.edit_menu.add_command(label="Paste and Take", command=self.paste_and_remove_from_clipboard_command,
                                   state="disabled")
        self.edit_menu.add_command(label="Delete selection", command=self.delete_selection_command, state="disabled")
        self.edit_menu.add_command(label="Clear document", command=self.clear_document_command)
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)
        self.move_menu = tk.Menu()
        self.move_menu.add_command(label="Cursor to document start", command=self.cursor_to_start_command)
        self.move_menu.add_command(label="Cursor to document end", command=self.cursor_to_end_command)
        self.menu_bar.add_cascade(label="Move", menu=self.move_menu)
        self.configure(menu=self.menu_bar)
        self.toolbar = tk.Frame(self, bd=2, relief=tk.RAISED)
        self.undo_button = tk.Button(self.toolbar, text="Undo", command=self.undo_command, state="disabled")
        self.undo_button.pack(side="left", expand=True, fill="both")
        self.redo_button = tk.Button(self.toolbar, text="Redo", command=self.redo_command, state="disabled")
        self.redo_button.pack(side="left", expand=True, fill="both")
        self.cut_button = tk.Button(self.toolbar, text="Cut", command=self.cut_command, state="disabled")
        self.cut_button.pack(side="left", expand=True, fill="both")
        self.copy_button = tk.Button(self.toolbar, text="Copy", command=self.copy_command, state="disabled")
        self.copy_button.pack(side="left", expand=True, fill="both")
        self.paste_button = tk.Button(self.toolbar, text="Paste", command=self.paste_command, state="disabled")
        self.paste_button.pack(side="left", expand=True, fill="both")
        self.toolbar.pack(side="top", fill="both")
        self.y_scroll = tk.Scrollbar(self)
        self.x_scroll = tk.Scrollbar(self, orient="horizontal")
        self.canvas = tk.Canvas(self, xscrollcommand=self.x_scroll.set, yscrollcommand=self.y_scroll.set, bg="white")
        self.y_scroll.config(command=self.canvas.yview)
        self.y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.x_scroll.config(command=self.canvas.xview)
        self.x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side="top", fill="both", expand=True)
        self.status_bar_text = tk.StringVar()
        self.status_bar_text.set("Cursor line: " + str(self.text_model.cursor_location.y + 1) +
                                 "   Cursor column: " + str(self.text_model.cursor_location.x + 1) +
                                 "   Number of lines: " + str(len(self.text_model.lines)))
        self.status_bar = tk.Label(self, textvariable=self.status_bar_text, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side="bottom", fill="both")
        self.plugins_menu = tk.Menu()
        self.load_plugins()
        self.menu_bar.add_cascade(label="Plugins", menu=self.plugins_menu)
        self.bind("<Left>", self.pressed_left)
        self.bind("<Up>", self.pressed_up)
        self.bind("<Right>", self.pressed_right)
        self.bind("<Down>", self.pressed_down)
        self.bind("<Return>", self.pressed_enter)
        self.bind("<BackSpace>", self.pressed_backspace)
        self.bind("<Delete>", self.pressed_delete)
        self.bind("<Shift-Up>", self.pressed_shift_up)
        self.bind("<Shift-Down>", self.pressed_shift_down)
        self.bind("<Shift-Right>", self.pressed_shift_right)
        self.bind("<Shift-Left>", self.pressed_shift_left)
        self.bind("<Key>", self.pressed_key)
        self.bind("<Control-c>", self.copy_command)
        self.bind("<Control-x>", self.cut_command)
        self.bind("<Control-v>", self.paste_command)
        self.bind("<Control-V>", self.paste_and_remove_from_clipboard_command)
        self.draw_text()
        self.draw_cursor()
        self.update()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def draw_text(self):
        x, y = self.indent_length, 0
        if self.text_model.has_selected():
            lines = list()
        for line in self.text_model.allLines():
            data = self.canvas.create_text(x, y, text=line, anchor=tk.NW)
            if self.text_model.has_selected():
                lines.append(data)
            y += self.font.metrics("linespace")
        if self.text_model.has_selected():
            r = self.text_model.getSelectionRange()
            if r.start.y == r.end.y:
                _, y1, _, y2 = self.canvas.bbox(lines[r.start.y])
                x1 = self.font.measure(self.text_model.lines[r.start.y][:r.start.x]) + self.indent_length
                x2 = self.font.measure(self.text_model.lines[r.end.y][:r.end.x + 1]) + self.indent_length
                self.canvas.tag_lower(self.canvas.create_rectangle(x1, y1, x2, y2, fill="blue", outline="blue"),
                                      lines[r.start.y])
            else:
                _, y1, _, y2 = self.canvas.bbox(lines[r.start.y])
                x1 = self.font.measure(self.text_model.lines[r.start.y][:r.start.x]) + self.indent_length
                x2 = self.font.measure(self.text_model.lines[r.start.y]) + self.indent_length
                self.canvas.tag_lower(self.canvas.create_rectangle(x1, y1, x2, y2, fill="blue", outline="blue"),
                                      lines[r.start.y])
                for i in range(r.start.y + 1, r.end.y):
                    _, y1, _, y2 = self.canvas.bbox(lines[i])
                    x1 = self.indent_length
                    x2 = self.font.measure(self.text_model.lines[i]) + self.indent_length
                    self.canvas.tag_lower(self.canvas.create_rectangle(x1, y1, x2, y2, fill="blue", outline="blue"),
                                          lines[i])
                _, y1, _, y2 = self.canvas.bbox(lines[r.end.y])
                x1 = self.indent_length
                x2 = self.font.measure(self.text_model.lines[r.end.y][:r.end.x + 1]) + self.indent_length
                self.canvas.tag_lower(self.canvas.create_rectangle(x1, y1, x2, y2, fill="blue", outline="blue"),
                                      lines[r.end.y])

    def draw_cursor(self):
        loc = self.text_model.cursor_location
        if loc.x == 0:
            x = self.indent_length
        else:
            x = self.indent_length + self.font.measure(self.text_model.lines[loc.y][:loc.x])
        y = loc.y * self.font.metrics("linespace")
        self.cursor = self.canvas.create_line(x, y, x, y + self.font.metrics("linespace"))

    def delete_cursor(self):
        self.canvas.delete(self.cursor)
        self.update()

    def pressed_up(self, event=None):
        self.text_model.clear_selection()
        self.text_model.moveCursorUp()

    def pressed_down(self, event=None):
        self.text_model.clear_selection()
        self.text_model.moveCursorDown()

    def pressed_left(self, event=None):
        self.text_model.clear_selection()
        self.text_model.moveCursorLeft()

    def pressed_right(self, event=None):
        self.text_model.clear_selection()
        self.text_model.moveCursorRight()

    def pressed_enter(self, event=None):
        self.text_model.clear_selection()
        self.text_model.enter_pressed()

    def pressed_backspace(self, event=None):
        if self.text_model.has_selected():
            self.text_model.deleteRange(self.text_model.getSelectionRange())
        else:
            self.text_model.deleteBefore()

    def pressed_delete(self, event=None):
        if self.text_model.has_selected():
            self.text_model.deleteRange(self.text_model.getSelectionRange())
        else:
            self.text_model.deleteAfter()

    def pressed_shift_up(self, event=None):
        if self.text_model.cursor_location.y == 0:
            return
        if self.text_model.has_selected():
            selection_range = self.text_model.getSelectionRange()
            self.text_model.moveCursorUp()
            if selection_range.start.y == selection_range.end.y:
                if self.text_model.cursor_location.x >= len(self.text_model.lines[self.text_model.cursor_location.y]):
                    start = Location(0, self.text_model.cursor_location.y + 1)
                else:
                    start = Location(self.text_model.cursor_location.x, self.text_model.cursor_location.y)
                end = selection_range.end
            elif self.text_model.cursor_location.y + 1 == selection_range.end.y:
                if selection_range.start.y == self.text_model.cursor_location.y and selection_range.start.x > \
                        self.text_model.cursor_location.x:
                    start = Location(self.text_model.cursor_location.x, self.text_model.cursor_location.y)
                    end = selection_range.start
                elif self.text_model.cursor_location.x - 1 < 0:
                    start = selection_range.start
                    end = Location(len(self.text_model.lines[self.text_model.cursor_location.y - 1]) - 1,
                                   self.text_model.cursor_location.y - 1)
                else:
                    start = selection_range.start
                    end = Location(self.text_model.cursor_location.x - 1, self.text_model.cursor_location.y)
            elif self.text_model.cursor_location.y == selection_range.end.y:
                start = selection_range.start
                end = Location(len(self.text_model.lines[self.text_model.cursor_location.y - 1]),
                               self.text_model.cursor_location.y - 1)
            else:
                if self.text_model.cursor_location.x >= len(self.text_model.lines[self.text_model.cursor_location.y]):
                    start = Location(0, self.text_model.cursor_location.y + 1)
                else:
                    start = Location(self.text_model.cursor_location.x, self.text_model.cursor_location.y)
                end = selection_range.end
        else:
            if self.text_model.cursor_location.x - 1 < 0:
                self.text_model.moveCursorUp()
                start = Location(0, self.text_model.cursor_location.y)
                end = Location(len(self.text_model.lines[self.text_model.cursor_location.y]) - 1,
                               self.text_model.cursor_location.y)
            else:
                end = Location(self.text_model.cursor_location.x - 1, self.text_model.cursor_location.y)
                self.text_model.moveCursorUp()
                if self.text_model.cursor_location.x >= len(self.text_model.lines[self.text_model.cursor_location.y]):
                    start = Location(0, self.text_model.cursor_location.y + 1)
                else:
                    start = Location(self.text_model.cursor_location.x, self.text_model.cursor_location.y)
        if start.y == end.y and start.x > end.x:
            self.text_model.clear_selection()
        else:
            self.text_model.setSelectionRange(LocationRange(start, end))

    def pressed_shift_down(self, event=None):
        if self.text_model.cursor_location.y + 1 >= len(self.text_model.lines):
            return
        if self.text_model.has_selected():
            selection_range = self.text_model.getSelectionRange()
            self.text_model.moveCursorDown()
            if selection_range.start.y == selection_range.end.y:
                start = selection_range.start
                if self.text_model.cursor_location.x - 1 < 0:
                    end = Location(len(self.text_model.lines[self.text_model.cursor_location.y - 1]) - 1,
                                   self.text_model.cursor_location.y - 1)
                else:
                    end = Location(self.text_model.cursor_location.x - 1, self.text_model.cursor_location.y)
            elif self.text_model.cursor_location.y - 1 == selection_range.start.y:
                if selection_range.end.y == self.text_model.cursor_location.y and selection_range.end.x < \
                        self.text_model.cursor_location.x:
                    start = selection_range.end
                    end = Location(self.text_model.cursor_location.x - 1, self.text_model.cursor_location.y)
                elif self.text_model.cursor_location.x >= len(
                        self.text_model.lines[self.text_model.cursor_location.y]):
                    start = Location(0, self.text_model.cursor_location.y + 1)
                    end = selection_range.end
                else:
                    start = Location(self.text_model.cursor_location.x, self.text_model.cursor_location.y)
                    end = selection_range.end
            elif self.text_model.cursor_location.y == selection_range.start.y:
                start = Location(0, self.text_model.cursor_location.y + 1)
                end = selection_range.end
            else:
                start = selection_range.start
                if self.text_model.cursor_location.x - 1 < 0:
                    end = Location(len(self.text_model.lines[self.text_model.cursor_location.y - 1]) - 1,
                                   self.text_model.cursor_location.y - 1)
                else:
                    end = Location(self.text_model.cursor_location.x - 1, self.text_model.cursor_location.y)
        else:
            if self.text_model.cursor_location.x - 1 < 0:
                start = Location(self.text_model.cursor_location.x, self.text_model.cursor_location.y)
                end = Location(len(self.text_model.lines[self.text_model.cursor_location.y]) - 1,
                               self.text_model.cursor_location.y)
                self.text_model.moveCursorDown()
            else:
                if self.text_model.cursor_location.x >= len(self.text_model.lines[self.text_model.cursor_location.y]):
                    start = Location(0, self.text_model.cursor_location.y + 1)
                else:
                    start = Location(self.text_model.cursor_location.x, self.text_model.cursor_location.y)
                self.text_model.moveCursorDown()
                end = Location(self.text_model.cursor_location.x - 1, self.text_model.cursor_location.y)
        if start.y == end.y and start.x > end.x:
            self.text_model.clear_selection()
        else:
            self.text_model.setSelectionRange(LocationRange(start, end))

    def pressed_shift_right(self, event=None):
        if self.text_model.cursor_location.x >= \
                len(self.text_model.lines[self.text_model.cursor_location.y]) and self.text_model.cursor_location.y \
                >= len(self.text_model.lines) - 1:
            return
        if self.text_model.has_selected():
            selection_range = self.text_model.getSelectionRange()
            if selection_range.start.y == self.text_model.cursor_location.y and selection_range.start.x == \
                    self.text_model.cursor_location.x:
                self.text_model.moveCursorRight()
                if self.text_model.cursor_location.x >= len(self.text_model.lines[self.text_model.cursor_location.y]):
                    if self.text_model.cursor_location.y >= len(self.text_model.lines) - 1:
                        self.text_model.clear_selection()
                        return
                    else:
                        start = Location(0, self.text_model.cursor_location.y + 1)
                        end = selection_range.end
                else:
                    start = Location(self.text_model.cursor_location.x, self.text_model.cursor_location.y)
                    end = selection_range.end
            else:
                self.text_model.moveCursorRight()
                if self.text_model.cursor_location.x - 1 < 0:
                    return
                else:
                    start = selection_range.start
                    end = Location(self.text_model.cursor_location.x - 1, self.text_model.cursor_location.y)
        else:
            if self.text_model.cursor_location.x >= len(self.text_model.lines[self.text_model.cursor_location.y]):
                self.text_model.moveCursorRight()
                return
            else:
                self.text_model.moveCursorRight()
                start = Location(self.text_model.cursor_location.x - 1, self.text_model.cursor_location.y)
                end = Location(self.text_model.cursor_location.x - 1, self.text_model.cursor_location.y)
        if start.y == end.y and start.x > end.x:
            self.text_model.clear_selection()
        else:
            self.text_model.setSelectionRange(LocationRange(start, end))

    def pressed_shift_left(self, event=None):
        if self.text_model.cursor_location.x - 1 < 0 and self.text_model.cursor_location.y == 0:
            return
        if self.text_model.has_selected():
            selection_range = self.text_model.getSelectionRange()
            if selection_range.end.y == self.text_model.cursor_location.y and selection_range.end.x == \
                    self.text_model.cursor_location.x - 1:
                self.text_model.moveCursorLeft()
                if self.text_model.cursor_location.x - 1 < 0:
                    if self.text_model.cursor_location.y == 0:
                        self.text_model.clear_selection()
                        return
                    else:
                        end = Location(len(self.text_model.lines[self.text_model.cursor_location.y - 1]) - 1,
                                       self.text_model.cursor_location.y - 1)
                else:
                    end = Location(self.text_model.cursor_location.x - 1, self.text_model.cursor_location.y)
                start = selection_range.start
            else:
                if self.text_model.cursor_location.x - 1 < 0:
                    self.text_model.moveCursorLeft()
                    return
                else:
                    self.text_model.moveCursorLeft()
                    start = Location(self.text_model.cursor_location.x, self.text_model.cursor_location.y)
                    end = selection_range.end
        else:
            if self.text_model.cursor_location.x - 1 < 0:
                self.text_model.moveCursorLeft()
                return
            else:
                self.text_model.moveCursorLeft()
                start = Location(self.text_model.cursor_location.x, self.text_model.cursor_location.y)
                end = Location(self.text_model.cursor_location.x, self.text_model.cursor_location.y)
        if start.y == end.y and start.x > end.x:
            self.text_model.clear_selection()
        else:
            self.text_model.setSelectionRange(LocationRange(start, end))

    def pressed_key(self, event):
        if not event.char:
            return
        if self.text_model.has_selected():
            self.text_model.deleteRange(self.text_model.getSelectionRange())
        self.text_model.insert_char(event.char)

    def copy_command(self, event=None):
        if self.text_model.has_selected():
            self.clipboard.push(self.text_model.get_selection())

    def cut_command(self, event=None):
        if self.text_model.has_selected():
            self.clipboard.push(self.text_model.get_selection())
            self.text_model.deleteRange(self.text_model.getSelectionRange())

    def paste_command(self, event=None):
        if not self.clipboard.is_empty():
            self.text_model.insert_text(self.clipboard.peek())

    def paste_and_remove_from_clipboard_command(self, event=None):
        if not self.clipboard.is_empty():
            self.text_model.insert_text(self.clipboard.pop())

    def undo_command(self, event=None):
        self.text_model.undo_manager.undo()

    def redo_command(self, event=None):
        self.text_model.undo_manager.redo()

    def open_command(self):
        self.opened_file = askopenfile(mode="r+", initialdir="/", title="Select text file",
                                       filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
        if self.opened_file is not None:
            lines = list()
            for line in self.opened_file:
                lines.append(line.rstrip())
            self.text_model.lines = lines
            self.text_model.cursor_location.x = 0
            self.text_model.cursor_location.y = 0
            self.text_model.notify_text_observers()
            self.text_model.notify_cursor_observers()

    def save_command(self):
        if self.opened_file is None:
            self.opened_file = asksaveasfile(mode="w+", title="Save file", defaultextension=".txt",
                                             filetypes=(("Text files", "*.txt"),))
        else:
            self.opened_file.seek(0)
            self.opened_file.truncate(0)
        if self.opened_file is not None:
            for line in self.text_model.lines:
                self.opened_file.write(line + "\n")
            self.opened_file.flush()

    def exit_command(self):
        if self.opened_file is not None:
            self.opened_file.close()
        self.destroy()

    def delete_selection_command(self):
        if self.text_model.has_selected():
            self.text_model.deleteRange(self.text_model.getSelectionRange())

    def clear_document_command(self):
        self.text_model.clear_all_text()

    def cursor_to_start_command(self):
        self.text_model.cursor_location.x = 0
        self.text_model.cursor_location.y = 0
        self.text_model.clear_selection()
        self.text_model.notify_cursor_observers()

    def cursor_to_end_command(self):
        if len(self.text_model.lines) > 0:
            self.text_model.cursor_location.x = len(self.text_model.lines[len(self.text_model.lines) - 1])
            self.text_model.cursor_location.y = len(self.text_model.lines) - 1
        else:
            self.text_model.cursor_location.x = 0
            self.text_model.cursor_location.y = 0
        self.text_model.clear_selection()
        self.text_model.notify_cursor_observers()

    def updateCursorLocation(self):
        self.canvas.delete("all")
        self.draw_text()
        self.draw_cursor()
        self.update()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.status_bar_text.set("Cursor line: " + str(self.text_model.cursor_location.y + 1) +
                                 "   Cursor column: " + str(self.text_model.cursor_location.x + 1) +
                                 "   Number of lines: " + str(len(self.text_model.lines)))

    def updateText(self):
        self.canvas.delete("all")
        self.draw_text()
        self.draw_cursor()
        self.update()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.status_bar_text.set("Cursor line: " + str(self.text_model.cursor_location.y + 1) +
                                 "   Cursor column: " + str(self.text_model.cursor_location.x + 1) +
                                 "   Number of lines: " + str(len(self.text_model.lines)))

    def update_clipboard(self, is_empty):
        if is_empty:
            self.edit_menu.entryconfig("Paste", state="disabled")
            self.edit_menu.entryconfig("Paste and Take", state="disabled")
            self.paste_button.config(state="disabled")
        else:
            self.edit_menu.entryconfig("Paste", state="normal")
            self.edit_menu.entryconfig("Paste and Take", state="normal")
            self.paste_button.config(state="normal")

    def update_undo_stack_status(self, is_empty):
        if is_empty:
            self.unbind("<Control-z>")
            self.edit_menu.entryconfig("Undo", state="disabled")
            self.undo_button.config(state="disabled")
        else:
            self.bind("<Control-z>", self.undo_command)
            self.edit_menu.entryconfig("Undo", state="normal")
            self.undo_button.config(state="normal")

    def update_redo_stack_status(self, is_empty):
        if is_empty:
            self.unbind("<Control-y>")
            self.edit_menu.entryconfig("Redo", state="disabled")
            self.redo_button.config(state="disabled")
        else:
            self.bind("<Control-y>", self.redo_command)
            self.edit_menu.entryconfig("Redo", state="normal")
            self.redo_button.config(state="normal")

    def updated_selection(self):
        if self.text_model.has_selected():
            self.edit_menu.entryconfig("Cut", state="normal")
            self.edit_menu.entryconfig("Copy", state="normal")
            self.edit_menu.entryconfig("Delete selection", state="normal")
            self.cut_button.config(state="normal")
            self.copy_button.config(state="normal")
        else:
            self.edit_menu.entryconfig("Cut", state="disabled")
            self.edit_menu.entryconfig("Copy", state="disabled")
            self.edit_menu.entryconfig("Delete selection", state="disabled")
            self.cut_button.config(state="disabled")
            self.copy_button.config(state="disabled")

    def load_plugins(self):
        for file in os.listdir('plugins_text_editor'):
            file_name, file_extension = os.path.splitext(file)
            if file_extension == '.py':
                module = import_module(file_name)
                self.add_plugin_to_menu(module)

    def add_plugin_to_menu(self, module):
        command = getattr(module, "execute")
        self.plugins_menu.add_command(label=getattr(module, "get_name")(),
                                      command=lambda: command(self, self.text_model.undo_manager, self.clipboard))


if __name__ == "__main__":
    sys.path.insert(0, './plugins_text_editor')
    model = TextEditorModel("Ovo je pokazni tekst.\nOvo je druga linija.")
    editor = TextEditor(model)
    editor.mainloop()
