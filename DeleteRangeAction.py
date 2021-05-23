from copy import deepcopy


class DeleteRangeAction:

    def __init__(self, model, r):
        self.model = model
        self.saved_lines = model.lines.copy()
        self.saved_cursor_location = deepcopy(model.cursor_location)
        self.r = r

    def execute_do(self):
        self.saved_lines = self.model.lines.copy()
        self.saved_cursor_location = deepcopy(self.model.cursor_location)
        if self.r.start.y == self.r.end.y:
            self.model.lines[self.r.start.y] = self.model.lines[self.r.start.y][:self.r.start.x] + self.model.lines[
                                                                                                       self.r.end.y][
                                                                                                   self.r.end.x + 1:]
        else:
            self.model.lines[self.r.start.y] = self.model.lines[self.r.start.y][:self.r.start.x]
            self.model.lines[self.r.end.y] = self.model.lines[self.r.end.y][self.r.end.x + 1:]
            self.model.lines = self.model.lines[:self.r.start.y + 1] + self.model.lines[self.r.end.y:]
            if not self.model.lines[self.r.start.y + 1]:
                del self.model.lines[self.r.start.y + 1]
        self.model.cursor_location.x = self.r.start.x
        self.model.cursor_location.y = self.r.start.y
        self.model.clear_selection()
        self.model.notify_text_observers()
        self.model.notify_cursor_observers()

    def execute_undo(self):
        self.model.lines = self.saved_lines.copy()
        self.model.cursor_location = deepcopy(self.saved_cursor_location)
        self.model.notify_text_observers()
        self.model.notify_cursor_observers()
