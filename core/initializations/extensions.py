import os
import importlib

EXTENSIONS_LOCATION = os.path.join(os.path.dirname(__file__), "../../extensions/")

# check if the extensions directory exists
if not os.path.exists(EXTENSIONS_LOCATION):
    os.makedirs(EXTENSIONS_LOCATION)

def get_extension_metadata(extension_name):
    metadata_file = os.path.join(EXTENSIONS_LOCATION, extension_name, "metadata.py")
    if os.path.exists(metadata_file):
        metadata_module = importlib.import_module(f"extensions.{extension_name}.metadata")
        return metadata_module
    
def list_extensions():
    extensions = []
    for item in os.listdir(EXTENSIONS_LOCATION):
        if os.path.isdir(os.path.join(EXTENSIONS_LOCATION, item)) and is_valid_extension(item):
            extensions.append(item)
    return extensions

def is_valid_extension(extension_name):
    init_file = os.path.join(EXTENSIONS_LOCATION, extension_name, "__init__.py")
    metadata_file = os.path.join(EXTENSIONS_LOCATION, extension_name, "metadata.py")
    return os.path.exists(init_file) and os.path.exists(metadata_file)

def register_extension(app, extension_name):
    metadata = get_extension_metadata(extension_name)
    bp = importlib.import_module(f"extensions.{extension_name}").bp
    app.register_blueprint(bp, url_prefix=metadata.URL_PREFIX, static_folder=metadata.STATIC_FOLDER, template_folder=metadata.TEMPLATE_FOLDER)

def register_all_extensions(app):
    for extension in list_extensions():
        register_extension(app, extension)