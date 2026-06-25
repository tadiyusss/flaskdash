from werkzeug.security import generate_password_hash, check_password_hash
from core.extensions import db
from flask_login import UserMixin
import uuid
import os
import enum

user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

class Role(db.Model):
    __table_args__ = (
        db.UniqueConstraint('name', name='uq_role_name'),
        db.UniqueConstraint('uid', name='uq_role_uid'),
    )
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), unique=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(200), nullable=True)

class UserRole(db.Model):
    __table_args__ = (
        db.UniqueConstraint('user_id', 'role_id', name='uq_user_role_user_role'),
    )

    __tablename__ = 'user_role'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    
    user = db.relationship('User', backref=db.backref('user_roles', cascade='all, delete-orphan'))
    role = db.relationship('Role', backref=db.backref('user_roles', cascade='all, delete-orphan'))


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
    password = db.Column(db.String(256), nullable=False)
    profile_image = db.Column(db.String(200), default='default-avatar.jpg')
    uid = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), unique=True)

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)
        db.session.commit()
        
    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)
    
    def has_role(self, role: str):
        return any(user_role.role.name == role for user_role in self.user_roles)

    def set_roles(self, roles: list):
        for user_role in self.user_roles:
            db.session.delete(user_role)

        for role_name in roles:
            role = Role.query.filter_by(name=role_name).first()
            if role:
                user_role = UserRole(user_id=self.id, role_id=role.id)
                db.session.add(user_role)

        db.session.commit()

    def delete_profile_image(self):
        if self.profile_image and self.profile_image != 'default-avatar.jpg':
            try:
                os.remove(os.path.join('core', 'static', 'images', 'profiles', self.profile_image))
            except FileNotFoundError:
                pass

    def delete_login_history(self):
        LoginHistory.query.filter_by(user_id=self.id).delete()
        db.session.commit()

    def __repr__(self):
        return f"<User {self.username} ({self.uid})>"

class LoginHistory(db.Model):
    __table_args__ = (
        db.UniqueConstraint('user_id', 'timestamp', name='uq_login_history_user_timestamp'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship('User', backref=db.backref('login_histories', cascade='all, delete-orphan'))
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    ip_address = db.Column(db.String(45), nullable=True)

    def __repr__(self):
        return f"<LoginHistory {self.user.username} at {self.timestamp}>"