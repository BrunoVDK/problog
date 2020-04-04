from MiniC2D import MiniC2D
from SDD import SDD


def create(package):
    package = package.lower()
    if package == "sdd":
        return SDD()
    elif package == "minic2d":
        return MiniC2D("")
    else:
        raise Exception("Unknown model counter")
