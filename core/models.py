from .extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import Enum
import enum

class User(db.Model, UserMixin): 
    __table_args__ = (
        db.UniqueConstraint('username', name='uq_user_username'),
        db.UniqueConstraint('email', name='uq_user_email'),
    )
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    profile_image = db.Column(db.String(200), default='default-avatar.jpg')

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)
    
    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)
    

class SettingsType(enum.Enum):
    text = 'text'
    textarea = 'textarea'
    bool = 'bool'
    number = 'number'
    email = 'email'
    url = 'url'
    datetime = 'datetime'

class Setting(db.Model):
    __table_args__ = (
        db.UniqueConstraint('name', name='uq_setting_name'),
        db.UniqueConstraint('key', name='uq_setting_key'),
    )
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    key = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(200), nullable=False)
    type = db.Column(Enum(SettingsType), nullable=False, default=SettingsType.text)
    description = db.Column(db.String(200), nullable=True)
    editable = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<Setting {self.name} ({self.key})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'key': self.key,
            'value': self.value,
            'type': self.type.value,
            'description': self.description,
            'editable': self.editable
        }