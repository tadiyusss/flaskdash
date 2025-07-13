from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from .styles import Style

style = Style()

class RegisterForm(FlaskForm):
    username = StringField('Username', 
        validators=[DataRequired(), Length(min=2, max=20)], 
        render_kw={"class": style.text_input}
    )
    email = StringField('Email', 
        validators=[DataRequired(), Email()],
        render_kw={"class": style.text_input}
    )
    password = PasswordField('Password', 
        validators=[DataRequired(), Length(min=6)],
        render_kw={"class": style.text_input}
    )
    retype_password = PasswordField('Confirm Password', 
        validators=[DataRequired(), Length(min=6)],
        render_kw={"class": style.text_input}
    )
    submit = SubmitField('Sign Up',
        render_kw={"class": style.button_full}
    )

class LoginForm(FlaskForm):
    email = StringField('Email', 
        validators=[DataRequired(), Email()],
        render_kw={"class": style.text_input}
    )
    password = PasswordField('Password', 
        validators=[DataRequired()],
        render_kw={"class": style.text_input}
    )
    submit = SubmitField('Login',
        render_kw={"class": style.button_full}
    )