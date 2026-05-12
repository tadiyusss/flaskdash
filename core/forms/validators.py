from core.models.users import User, Role
from wtforms import ValidationError
from flask_login import current_user


def validate_my_username_unique(form, field):
    if current_user.username != field.data and User.query.filter_by(username=field.data).first():
        raise ValidationError('Username already exists.')
    
def validate_my_email_unique(form, field):
    if current_user.email != field.data and User.query.filter_by(email=field.data).first():
        raise ValidationError('Email already exists.')
    
def validate_username_unique(form, field):
    if User.query.filter_by(username=field.data).first():
        raise ValidationError('Username already exists.')

def validate_email_unique(form, field):
    if User.query.filter_by(email=field.data).first():
        raise ValidationError('Email already exists.')
    
def validate_role_name_unique(form, field):
    if Role.query.filter_by(name=field.data).first():
        raise ValidationError('Role name already exists.')

def validate_password_length(form, field):
    if len(field.data) < 8:
        raise ValidationError('Password must be at least 8 characters long.')
    
def validate_password_uppercase_letter(form, field):
    if not any(char.isupper() for char in field.data):
        raise ValidationError('Password must contain at least one uppercase letter.')

def validate_password_lowercase_letter(form, field):
    if not any(char.islower() for char in field.data):
        raise ValidationError('Password must contain at least one lowercase letter.')
    
def validate_password_digit(form, field):
    if not any(char.isdigit() for char in field.data):
        raise ValidationError('Password must contain at least one digit.')