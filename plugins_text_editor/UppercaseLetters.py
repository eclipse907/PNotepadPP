import re


def get_name():
    return "Uppercase letters"


def get_description():
    return "Makes all the first letters in the words of the text file uppercase."


def execute(text_editor, undoManager, clipboardStack):
    action = UppercaseLettersAction(text_editor.text_model)
    action.execute_do()
    undoManager.push(action)


class UppercaseLettersAction:

    def __init__(self, model):
        self.model = model
        self.saved_lines = model.lines.copy()

    def execute_do(self):
        new_lines = list()
        for line in self.model.lines:
            new_lines.append(re.sub(r"(^|\s)(\S)", lambda m: m.group(1) + m.group(2).upper(), line))
        self.model.lines = new_lines
        self.model.notify_text_observers()

    def execute_undo(self):
        self.model.lines = self.saved_lines.copy()
        self.model.notify_text_observers()
