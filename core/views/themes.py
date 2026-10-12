from flask import render_template, abort
from flask_login import login_required
from core.utils.decorators import developer_mode_required, role_required
from core.route import core
from core.utils.registry.themes import get_all_themes

@core.route('/themes', methods=['GET'])
@login_required
@role_required('Administrator')
@developer_mode_required()
def themes():
    themes = get_all_themes()
    return render_template('dashboard/themes.html', themes=themes)

@core.route('/themes/view/<string:name>', methods=['GET'])
@login_required
@role_required('Administrator')
@developer_mode_required()
def view_theme(name):
    themes = get_all_themes()

    if not name:
        abort(404)

    theme = next((t for t in themes if t.name == name), None)
    if not theme:
        abort(404)

    
    return render_template('dashboard/view_theme.html', theme=theme)
