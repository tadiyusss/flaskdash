import os
import importlib
from core.utils.registry.extensions import get_extension_metadata, list_extensions, register_extension

def include_extension(app, extension_name):
    metadata = get_extension_metadata(extension_name)
    bp = importlib.import_module(f"extensions.{extension_name}").bp
    app.register_blueprint(bp, url_prefix=metadata.URL_PREFIX, static_folder=metadata.STATIC_FOLDER, template_folder=metadata.TEMPLATE_FOLDER)

def include_all_extensions(app):
    for extension in list_extensions():
        print(f"Including extension: {extension}")
        register_extension(extension)
        include_extension(app, extension)