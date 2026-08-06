from flask import render_template, abort
from flask_login import login_required
from core.extensions import db
from core.utils.decorators import role_required
from core.route import core
import os
from core.defaults import THEMES_DIR
from core.utils.themes import list_themes, get_theme_info

@core.route('/themes', methods=['GET'])
@role_required('Administrator')
@login_required
def themes():
    themes = list_themes()
    return render_template('dashboard/themes.html', themes=themes)

@core.route('/themes/view/<string:name>', methods=['GET'])
@role_required('Administrator')
@login_required
def view_theme(name):
    if name not in list_themes():
        return abort(404)

    theme_info = get_theme_info(name)
    return render_template('dashboard/view_theme.html', theme_info = theme_info)
