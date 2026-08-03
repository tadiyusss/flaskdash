from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, Length
from .validators import validate_email_unique, validate_username_unique, validate_password_length, validate_password_uppercase_letter, validate_password_lowercase_letter, validate_password_digit

class LoginForm(FlaskForm):
    email = EmailField('Email Address', 
        validators=[DataRequired(message="Email is required"), Email(message="Enter a valid email")],
        render_kw={
            "class": "fd-input-group-field",
            "placeholder": "you@company.com"
        },
    )
    password = PasswordField('Password', 
        validators=[DataRequired(message="Password is required")],
        render_kw={
            "class": "fd-input-group-field fd-input-group-field-sm",
            "placeholder": "Your password",
            ":type": "show ? 'text' : 'password'"
        }
    )

class RegisterForm(FlaskForm):
    firstname = StringField('First Name',
        validators=[DataRequired(message="First name is required"), Length(min=2, max=30)],
        render_kw={
            "class": "fd-input",
            "placeholder": "John"
        }
    )

    lastname = StringField('Last Name',
        validators=[DataRequired(message="Last name is required"), Length(min=2, max=30)],
        render_kw={
            "class": "fd-input",
            "placeholder": "Doe"
        }
    )

    username = StringField('Username', 
        validators=[DataRequired(message="Username is required"), Length(min=2, max=20), validate_username_unique], 
        render_kw={
            "class": "fd-input",
            "placeholder": "johndoe"
        }
    )
    email = StringField('Email Address', 
        validators=[DataRequired(message="Email is required"), Email(message="Enter a valid email"), validate_email_unique],
        render_kw={
            "class": "fd-input-group-field",
            "placeholder": "you@company.com"
        }
    )
    password = PasswordField('Password', 
        validators=[DataRequired(message="Password is required"), Length(min=6),validate_password_length, validate_password_uppercase_letter, validate_password_lowercase_letter, validate_password_digit],
        render_kw={
            "class": "fd-input-group-field",
            "placeholder": "••••••••",
            ":type": "show ? 'text' : 'password'",
            "x-model": "password"
        }
    )
    retype_password = PasswordField('Confirm Password', 
        validators=[DataRequired(message="Please confirm your password"), Length(min=6)],
        render_kw={
            "class": "fd-input-group-field",
            "placeholder": "••••••••",
            ":type": "showC ? 'text' : 'password'",
            "x-model": "confirm"
        }
    )
    submit = SubmitField('Sign Up',
        render_kw={"class": "btn-full"}
    )

class ForgotPasswordForm(FlaskForm):
    email = EmailField('Email Address', 
        validators=[DataRequired(message="Email is required"), Email(message="Enter a valid email")],
        render_kw={
            "class": "fd-input-group-field",
            "placeholder": "you@company.com"
        }
    )

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', 
        validators=[DataRequired(message="Password is required"), Length(min=6), validate_password_length, validate_password_uppercase_letter, validate_password_lowercase_letter, validate_password_digit],
        render_kw={
            "class": "fd-input-group-field",
            "placeholder": "••••••••",
            ":type": "showNew ? 'text' : 'password'"
        }
    )
    retype_password = PasswordField('Confirm New Password', 
        validators=[DataRequired(message="Please confirm your password"), Length(min=6)],
        render_kw={
            "class": "fd-input-group-field",
            "placeholder": "••••••••",
            ":type": "showConfirm ? 'text' : 'password'"
        }
    )