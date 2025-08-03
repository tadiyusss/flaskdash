from core.extensions import db

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

    def __repr__(self):
        return f"<Setting {self.name} ({self.key})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'key': self.key,
            'value': self.value,
        }
    