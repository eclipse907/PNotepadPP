from UndoManager import UndoManager
from DeleteBeforeAction import DeleteBeforeAction
from DeleteAfterAction import DeleteAfterAction
from DeleteRangeAction import DeleteRangeAction
from EnterPressedAction import EnterPressedAction
from InsertCharAction import InsertCharAction
from InsertTextAction import InsertTextAction
from ClearAllTextAction import ClearAllTextAction


class Location:

    def __init__(self, x, y):
        self.x = x
        self.y = y


class LocationRange:

    def __init__(self, start, end):
        self.start = start
        self.end = end


class TextEditorModel:

    def __init__(self, text):
        self.lines = text.splitlines()
        self.cursor_location = Location(0, 0)
        self.selection_range = None
        self.cursor_observers = set()
        self.text_observers = set()
        self.selection_observers = set()
        self.undo_manager = UndoManager()

    def allLines(self):
        return (line for line in self.lines)

    def linesRange(self, index1, index2):
        return (line for line in self.lines[index1:index2])

    def moveCursorLeft(self):
        if self.cursor_location.x == 0 and self.cursor_location.y == 0:
            return
        elif self.cursor_location.x == 0:
            self.cursor_location.x = len(self.lines[self.cursor_location.y - 1])
            self.cursor_location.y -= 1
        else:
            self.cursor_location.x -= 1
        self.notify_cursor_observers()

    def moveCursorRight(self):
        if self.cursor_location.y == len(self.lines) - 1 and self.cursor_location.x == \
                len(self.lines[self.cursor_location.y]):
            return
        elif self.cursor_location.x == len(self.lines[self.cursor_location.y]):
            self.cursor_location.x = 0
            self.cursor_location.y += 1
        else:
            self.cursor_location.x += 1
        self.notify_cursor_observers()

    def moveCursorUp(self):
        if self.cursor_location.y == 0:
            return
        else:
            self.cursor_location.y -= 1
            if self.cursor_location.x > len(self.lines[self.cursor_location.y]):
                self.cursor_location.x = len(self.lines[self.cursor_location.y])
        self.notify_cursor_observers()

    def moveCursorDown(self):
        if self.cursor_location.y == len(self.lines) - 1:
            return
        else:
            self.cursor_location.y += 1
            if self.cursor_location.x > len(self.lines[self.cursor_location.y]):
                self.cursor_location.x = len(self.lines[self.cursor_location.y])
        self.notify_cursor_observers()

    def deleteBefore(self):
        action = DeleteBeforeAction(self)
        action.execute_do()
        self.undo_manager.push(action)

    def deleteAfter(self):
        action = DeleteAfterAction(self)
        action.execute_do()
        self.undo_manager.push(action)

    def deleteRange(self, r):
        action = DeleteRangeAction(self, r)
        action.execute_do()
        self.undo_manager.push(action)

    def getSelectionRange(self):
        return self.selection_range

    def setSelectionRange(self, r):
        self.selection_range = r
        self.notify_text_observers()
        self.notify_selection_observers()

    def enter_pressed(self):
        action = EnterPressedAction(self)
        action.execute_do()
        self.undo_manager.push(action)

    def has_selected(self):
        return self.selection_range is not None

    def insert_char(self, c):
        action = InsertCharAction(self, c)
        action.execute_do()
        self.undo_manager.push(action)

    def insert_text(self, text):
        action = InsertTextAction(self, text)
        action.execute_do()
        self.undo_manager.push(action)

    def get_selection(self):
        if not self.has_selected():
            return ""
        start = self.selection_range.start
        end = self.selection_range.end
        if start.y == end.y:
            return self.lines[start.y][start.x:end.x + 1]
        else:
            text = self.lines[start.y][start.x:]
            for i in range(start.y + 1, end.y):
                text += self.lines[i]
            text += self.lines[end.y][:end.x + 1]
            return text

    def clear_selection(self):
        self.selection_range = None
        self.notify_text_observers()
        self.notify_selection_observers()

    def clear_all_text(self):
        action = ClearAllTextAction(self)
        action.execute_do()
        self.undo_manager.push(action)

    def add_cursor_observer(self, observer):
        self.cursor_observers.add(observer)

    def remove_cursor_observer(self, observer):
        self.cursor_observers.discard(observer)

    def notify_cursor_observers(self):
        for observer in self.cursor_observers:
            observer.updateCursorLocation()

    def add_text_observer(self, observer):
        self.text_observers.add(observer)

    def remove_text_observer(self, observer):
        self.text_observers.discard(observer)

    def notify_text_observers(self):
        for observer in self.text_observers:
            observer.updateText()

    def add_selection_observer(self, observer):
        self.selection_observers.add(observer)

    def remove_selection_observer(self, observer):
        self.selection_observers.discard(observer)

    def notify_selection_observers(self):
        for observer in self.selection_observers:
            observer.updated_selection()
