import os 
from core.models.users import User, LoginHistory
from datetime import datetime, timedelta
from sqlalchemy import func, distinct

def get_total_users():
    return User.query.count()

def get_active_users():
    seven_days_ago = datetime.now() - timedelta(days=7)
    logins = LoginHistory.query.filter(LoginHistory.timestamp >= seven_days_ago)
    return logins.with_entities(func.count(distinct(LoginHistory.user_id))).scalar()

def get_uploads_storage_usage():
    total_size = 0
    uploads_path = os.path.join('core', 'static', 'uploads')
    for dirpath, dirnames, filenames in os.walk(uploads_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if os.path.isfile(file_path):
                total_size += os.path.getsize(file_path)
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if total_size < 1024:
            return f"{total_size:.2f} {unit}"
        total_size /= 1024
    