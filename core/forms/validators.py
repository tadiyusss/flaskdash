from core.models import User
from wtforms import ValidationError
from flask_login import current_user


def validate_username_unique(form, field):
    if current_user.username != field.data and User.query.filter_by(username=field.data).first():
        raise ValidationError('Username already exists.')
    
def validate_email_unique(form, field):
    if current_user.email != field.data and User.query.filter_by(email=field.data).first():
        raise ValidationError('Email already exists.')