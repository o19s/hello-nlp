import imp
import os

MainModule = "__init__"

def get_plugins(root):
    plugins = []
    possible = os.listdir(root)
    filename = MainModule + ".py"
    for i in possible:
        location = os.path.join(root, i)
        if not os.path.isdir(location) or not filename in os.listdir(location):
            continue
        info = imp.find_module(MainModule, [location])
        plugins.append({"name": i, "info": info})
    return plugins

def load_plugin(plugin):
    return imp.load_module(MainModule, *plugin["info"])
