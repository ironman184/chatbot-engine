import pkgutil
import importlib
import actions

def load_all_actions():
    for module in pkgutil.iter_modules(actions.__path__):
        importlib.import_module(f"actions.{module.name}")
