import sys


def cleanup_modules(modules):
    for module in modules:
        if module in sys.modules:
            del sys.modules[module]
