from copy import deepcopy


class InsertCharAction:

    def __init__(self, model, c):
        self.model = model
        self.saved_lines = model.lines.copy()
        self.saved_cursor_location = deepcopy(model.cursor_location)
        self.c = c

    def execute_do(self):
        self.saved_lines = self.model.lines.copy()
        self.saved_cursor_location = deepcopy(self.model.cursor_location)
        if not self.model.lines:
            self.model.lines.append(self.c)
        else:
            self.model.lines[self.model.cursor_location.y] =\
                self.model.lines[self.model.cursor_location.y][:self.model.cursor_location.x] + self.c + \
                self.model.lines[self.model.cursor_location.y][self.model.cursor_location.x:]
        self.model.moveCursorRight()
        self.model.notify_text_observers()

    def execute_undo(self):
        self.model.lines = self.saved_lines.copy()
        self.model.cursor_location = deepcopy(self.saved_cursor_location)
        self.model.notify_text_observers()
        self.model.notify_cursor_observers()
