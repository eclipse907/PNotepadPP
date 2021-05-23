class Tiger:
    def __init__(self, name):
        self.ime = name
        self.greeting = "Mijau!"
        self.meni = "mlako mlijeko"

    def name(self):
        return self.ime

    def greet(self):
        return self.greeting

    def menu(self):
        return self.meni


def create(name):
    return Tiger(name)
