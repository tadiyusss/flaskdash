from flask import render_template
from flask_login import login_required
from core.extensions import db
from core.utils.decorators import role_required
from core.route import core
import os
from core.defaults import THEMES_DIR
from core.utils.themes import list_themes

@core.route('/themes', methods=['GET'])
@role_required('Administrator')
@login_required
def themes():
    themes = list_themes()
    return render_template('dashboard/themes.html', themes=themes)