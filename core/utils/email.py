from flask_mail import Message
from core.extensions import mail
from flask import url_for
from .tokens import generate_reset_token

def send_password_reset_email(user):
    token = generate_reset_token(user)
    message = Message("Password Reset Instructions", recipients=[user.email])
    message.body = f"Hello {user.firstname},\n\nTo reset your password, please click the following link:\n\n{url_for('core.reset_password', token=token, _external=True)}\n\nIf you did not request a password reset, please ignore this email.\n\nBest regards,\nFlaskDash Team"
    mail.send(message)  