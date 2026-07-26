from core.route import system
from flask import g, send_file, abort
from pathlib import Path

@system.route('/favicon.ico')
def show_favicon():
    
    filename = g.settings['favicon_icon']

    if filename == "" or filename is None:
        abort(404)

    media_folder = Path(__file__).resolve().parent.parent.parent / 'media'

    file_path = media_folder / filename
    if not file_path.exists():
        abort(404)

    return send_file(str(file_path), mimetype='image/x-icon')