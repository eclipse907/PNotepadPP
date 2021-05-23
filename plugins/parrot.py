class Parrot:
    def __init__(self, name):
        self.ime = name
        self.greeting = "Sto mu gromova!"
        self.meni = "brazilske orahe"

    def name(self):
        return self.ime

    def greet(self):
        return self.greeting

    def menu(self):
        return self.meni


def create(name):
    return Parrot(name)
