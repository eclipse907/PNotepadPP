class ClipboardStack:

    def __init__(self):
        self.stack_texts = list()
        self.clipboard_observers = set()

    def push(self, text):
        self.stack_texts.append(text)
        self.notify_all_observers()

    def pop(self):
        text = self.stack_texts.pop()
        self.notify_all_observers()
        return text

    def peek(self):
        return self.stack_texts[-1]

    def is_empty(self):
        if not self.stack_texts:
            return True
        else:
            return False

    def clear_stack(self):
        self.stack_texts.clear()
        self.notify_all_observers()

    def add_clipboard_observer(self, observer):
        self.clipboard_observers.add(observer)

    def remove_clipboard_observer(self, observer):
        self.clipboard_observers.discard(observer)

    def notify_all_observers(self):
        if not self.stack_texts:
            is_empty = True
        else:
            is_empty = False
        for observer in self.clipboard_observers:
            observer.update_clipboard(is_empty)
