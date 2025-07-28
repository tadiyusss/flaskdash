"""
This module registers and manages metadata of extensions.
"""
import importlib
import os 

EXTENSIONS_LOCATION = os.path.join(os.path.dirname(__file__), "../../../extensions/")
EXTENSIONS_METADATA = []

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

def register_extension(name):
    metadata = get_extension_metadata(name)
    if metadata:
        EXTENSIONS_METADATA.append({
            "name": metadata.NAME,
            "version": metadata.VERSION,
            "description": metadata.DESCRIPTION,
            "author": metadata.AUTHOR,
            "url_prefix": metadata.URL_PREFIX,
            "static_folder": metadata.STATIC_FOLDER,
            "template_folder": metadata.TEMPLATE_FOLDER
        })

def get_registered_extension_metadata(name):
    for ext in EXTENSIONS_METADATA:
        if ext["name"] == name:
            return ext
    return None
    