import re
from tkinter.messagebox import showinfo


def get_name():
    return "Statistics"


def get_description():
    return "Counts the number of lines, words and letters in the text file and displays it in a dialog."


def execute(text_editor, undoManager, clipboardStack):
    num_of_lines = len(text_editor.text_model.lines)
    num_of_words = 0
    num_of_letters = 0
    for line in text_editor.text_model.lines:
        num_of_words += len(re.findall(r'\w+', line))
        num_of_letters += len(re.findall(r'[a-zA-Z]', line))
    showinfo("Text file statistics", "There are " + str(num_of_lines) + " lines, " + str(num_of_words) + " words and " +
             str(num_of_letters) + " letters in this text file.")
