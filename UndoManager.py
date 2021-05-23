class UndoManager:

    class __Singleton:

        def __init__(self):
            self.undo_stack = list()
            self.redo_stack = list()
            self.undo_stack_observers = set()
            self.redo_stack_observers = set()

        def __str__(self):
            return repr(self)

        def undo(self):
            command = self.undo_stack.pop()
            if not self.undo_stack:
                self.notify_undo_stack_observers()
            command.execute_undo()
            if not self.redo_stack:
                self.redo_stack.append(command)
                self.notify_redo_stack_observers()
            else:
                self.redo_stack.append(command)

        def redo(self):
            command = self.redo_stack.pop()
            if not self.redo_stack:
                self.notify_redo_stack_observers()
            command.execute_do()
            if not self.undo_stack:
                self.undo_stack.append(command)
                self.notify_undo_stack_observers()
            else:
                self.undo_stack.append(command)

        def push(self, c):
            self.redo_stack.clear()
            self.notify_redo_stack_observers()
            if not self.undo_stack:
                self.undo_stack.append(c)
                self.notify_undo_stack_observers()
            else:
                self.undo_stack.append(c)

        def add_undo_stack_observer(self, observer):
            self.undo_stack_observers.add(observer)

        def remove_undo_stack_observer(self, observer):
            self.undo_stack_observers.discard(observer)

        def notify_undo_stack_observers(self):
            if not self.undo_stack:
                is_empty = True
            else:
                is_empty = False
            for observer in self.undo_stack_observers:
                observer.update_undo_stack_status(is_empty)

        def add_redo_stack_observer(self, observer):
            self.redo_stack_observers.add(observer)

        def remove_redo_stack_observer(self, observer):
            self.redo_stack_observers.discard(observer)

        def notify_redo_stack_observers(self):
            if not self.redo_stack:
                is_empty = True
            else:
                is_empty = False
            for observer in self.redo_stack_observers:
                observer.update_redo_stack_status(is_empty)

    instance = None

    def __init__(self):
        if not UndoManager.instance:
            UndoManager.instance = UndoManager.__Singleton()

    def __getattr__(self, name):
        return getattr(self.instance, name)
