from copy import deepcopy


class InsertTextAction:

    def __init__(self, model, text):
        self.model = model
        self.saved_lines = model.lines.copy()
        self.saved_cursor_location = deepcopy(model.cursor_location)
        self.text = text

    def execute_do(self):
        self.saved_lines = self.model.lines.copy()
        self.saved_cursor_location = deepcopy(self.model.cursor_location)
        text = self.text.splitlines()
        if not self.model.lines:
            for line in text:
                self.model.lines.append(line)
            self.model.cursor_location.x = len(text[len(text) - 1])
            self.model.cursor_location.y = len(text) - 1
        elif len(text) == 1:
            self.model.lines[self.model.cursor_location.y] =\
                self.model.lines[self.model.cursor_location.y][:self.model.cursor_location.x] + text[0] + \
                self.model.lines[self.model.cursor_location.y][self.model.cursor_location.x:]
            self.model.cursor_location.x += len(text[0])
        else:
            old_first_line = self.model.lines[self.model.cursor_location.y]
            self.model.lines[self.model.cursor_location.y] = old_first_line[:self.model.cursor_location.x] + text[0]
            insert_index = self.model.cursor_location.y + 1
            for i in range(1, len(text) - 1):
                self.model.lines.insert(insert_index, text[i])
                insert_index += 1
            last_line = text[len(text) - 1] + old_first_line[self.model.cursor_location.x:]
            self.model.lines.insert(insert_index, last_line)
            self.model.cursor_location.x = len(text[len(text) - 1])
            self.model.cursor_location.y = insert_index
        self.model.notify_text_observers()
        self.model.notify_cursor_observers()

    def execute_undo(self):
        self.model.lines = self.saved_lines.copy()
        self.model.cursor_location = deepcopy(self.saved_cursor_location)
        self.model.notify_text_observers()
        self.model.notify_cursor_observers()
