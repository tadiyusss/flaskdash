from core.route import system
from flask import g, send_file, abort
import os

@system.route('/favicon.ico')
def show_favicon():
    
    filename = g.settings['favicon_icon']

    if filename == "" or filename is None:
        abort(404)

    media_folder = os.path.join(os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..')), 'media')
    return send_file(os.path.join(media_folder, filename), mimetype='image/x-icon')