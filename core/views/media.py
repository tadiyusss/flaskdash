from core.route import media
from flask import send_from_directory

@media.route('/media/<path:filename>', methods=['GET'])
def serve_media(filename):
    return send_from_directory('../media', filename)