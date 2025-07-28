from flask import render_template
from flask_login import login_required, current_user
from core.utils.registry import analytics

def generate_routes(core):
    @core.route('/home')
    @login_required
    def dashboard():
        analytics_items = analytics.get_analytics_items(current_user)
        return render_template('dashboard/home.html', user=current_user, analytics_items=analytics_items)