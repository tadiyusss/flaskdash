from core.extensions import db
import enum
from sqlalchemy import Enum


class SettingsType(enum.Enum):
    text = 'text'
    textarea = 'textarea'
    bool = 'bool'
    number = 'number'
    email = 'email'
    url = 'url'
    datetime = 'datetime'
    select = 'select'
    radio = 'radio'

class SettingCategory(db.Model):
    __table_args__ = (
        db.UniqueConstraint('name', name='uq_setting_category_name'),
    )
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    nice_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f"<SettingCategory {self.name}>"

class Setting(db.Model):
    __table_args__ = (
        db.UniqueConstraint('name', name='uq_setting_name'),
        db.UniqueConstraint('key', name='uq_setting_key'),
    )
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), db.ForeignKey('setting_category.name'), nullable=False)
    category = db.relationship('SettingCategory', backref='settings', lazy=True)
    name = db.Column(db.String(100), nullable=False)
    key = db.Column(db.String(100), nullable=False, unique=True)
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

class SettingChoices(db.Model):
    __table_args__ = (
        db.UniqueConstraint('setting_key', 'value', name='uq_setting_choice'),
    )
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(100), db.ForeignKey('setting.key'), nullable=False)
    value = db.Column(db.String(100), nullable=False)
    label = db.Column(db.String(100), nullable=False)
    