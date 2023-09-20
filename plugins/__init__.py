# Pardon this abomination xD
def get_plugins():
    import importlib
    import os

    def modulename_to_classname(modulename):
        return "".join(c.capitalize() for c in modulename.lower().split("_"))
    
    plugins_path = os.path.dirname(__file__)
    plugin_files = [f for f in os.listdir(plugins_path) if f.endswith('.py') and f != '__init__.py']
    plugin_modules = [importlib.import_module(f'plugins.{plugin_file[:-3]}') for plugin_file in plugin_files]
    plugins_classes = [getattr(p, modulename_to_classname(p.__name__.split('.')[-1])) for p in plugin_modules]
    
    return plugins_classes
