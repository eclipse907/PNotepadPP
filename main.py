import os
import sys
from importlib import import_module


def myfactory(module_name):
    try:
        module = import_module(module_name)
        return getattr(module, "create")
    except ImportError:
        print("Can not load the module name given.")
        exit(1)
    except AttributeError:
        print("Can not load the attribute name given.")
        exit(1)


def printGreeting(pet):
    print("%s pozdravlja: %s" % (pet.name(), pet.greet()))


def printMenu(pet):
    print("%s voli %s." % (pet.name(), pet.menu()))


def test():
    pets = []
    # obiđi svaku datoteku kazala plugins
    for mymodule in os.listdir('plugins'):
        moduleName, moduleExt = os.path.splitext(mymodule)
        # ako se radi o datoteci s Pythonskim kodom ...
        if moduleExt == '.py':
            # instanciraj ljubimca ...
            ljubimac = myfactory(moduleName)('Ljubimac ' + str(len(pets)))
            # ... i dodaj ga u listu ljubimaca
            pets.append(ljubimac)

    # ispiši ljubimce
    for pet in pets:
        printGreeting(pet)
        printMenu(pet)


if __name__ == "__main__":
    sys.path.insert(0, './plugins')
    test()
