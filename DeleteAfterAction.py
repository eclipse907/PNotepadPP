class DeleteAfterAction:

    def __init__(self, model):
        self.model = model
        self.saved_lines = model.lines.copy()

    def execute_do(self):
        self.saved_lines = self.model.lines.copy()
        if self.model.cursor_location.x >= len(self.model.lines[self.model.cursor_location.y]):
            return
        else:
            self.model.lines[self.model.cursor_location.y] = \
                self.model.lines[self.model.cursor_location.y][:self.model.cursor_location.x] + \
                self.model.lines[self.model.cursor_location.y][self.model.cursor_location.x + 1:]
        self.model.notify_text_observers()

    def execute_undo(self):
        self.model.lines = self.saved_lines.copy()
        self.model.notify_text_observers()
