from .extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import Enum
import uuid
import enum


user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(200), nullable=True)

class User(db.Model, UserMixin): 
    __table_args__ = (
        db.UniqueConstraint('username', name='uq_user_username'),
        db.UniqueConstraint('email', name='uq_user_email'),
        db.UniqueConstraint('uid', name='uq_user_uid'),
    )
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    firstname = db.Column(db.String(100), nullable=True)
    lastname = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    profile_image = db.Column(db.String(200), default='default-avatar.jpg')
    role = db.Column(db.String(50), default='viewer')
    uid = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), unique=True)

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

    @staticmethod
    def create_or_update(name, key, value, type=SettingsType.text, description=None, editable=True):
        setting = Setting.query.filter_by(key=key).first()
        if setting:
            setting.name = name
            setting.value = value
            setting.type = type
            setting.description = description
            setting.editable = editable
        else:
            setting = Setting(
                name=name,
                key=key,
                value=value,
                type=type,
                description=description,
                editable=editable
            )
            db.session.add(setting)
        db.session.commit()
        return setting
    
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