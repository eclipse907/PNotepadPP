from copy import deepcopy


class EnterPressedAction:

    def __init__(self, model):
        self.model = model
        self.saved_lines = model.lines.copy()
        self.saved_cursor_location = deepcopy(model.cursor_location)

    def execute_do(self):
        self.saved_lines = self.model.lines.copy()
        self.saved_cursor_location = deepcopy(self.model.cursor_location)
        self.model.lines.insert(self.model.cursor_location.y + 1,
                                self.model.lines[self.model.cursor_location.y][self.model.cursor_location.x:])
        self.model.lines[self.model.cursor_location.y] = \
            self.model.lines[self.model.cursor_location.y][:self.model.cursor_location.x]
        self.model.cursor_location.y += 1
        self.model.cursor_location.x = 0
        self.model.notify_text_observers()
        self.model.notify_cursor_observers()

    def execute_undo(self):
        self.model.lines = self.saved_lines.copy()
        self.model.cursor_location = deepcopy(self.saved_cursor_location)
        self.model.notify_text_observers()
        self.model.notify_cursor_observers()
