import os
import importlib
from core.utils.registry.extensions import get_extension_metadata, list_extensions, register_extension
from core.extensions import db

def include_extension(app, extension_name):
    extension = importlib.import_module(f"extensions.{extension_name}").init_extension(app, db)
    app.register_blueprint(extension)

def include_all_extensions(app):
    for extension in list_extensions():
        register_extension(extension)
        include_extension(app, extension)