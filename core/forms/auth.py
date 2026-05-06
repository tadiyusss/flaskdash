from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    email = StringField('Email', 
        validators=[DataRequired(), Email()],
        render_kw={"class": "text-input"}
    )
    password = PasswordField('Password', 
        validators=[DataRequired()],
        render_kw={"class": "text-input"}
    )
    submit = SubmitField('Login',
        render_kw={"class": "btn"}
    )

class RegisterForm(FlaskForm):
    username = StringField('Username', 
        validators=[DataRequired(), Length(min=2, max=20)], 
        render_kw={"class": "text-input"}
    )
    email = StringField('Email', 
        validators=[DataRequired(), Email()],
        render_kw={"class": "text-input"}
    )
    password = PasswordField('Password', 
        validators=[DataRequired(), Length(min=6)],
        render_kw={"class": "text-input"}
    )
    retype_password = PasswordField('Confirm Password', 
        validators=[DataRequired(), Length(min=6)],
        render_kw={"class": "text-input"}
    )
    submit = SubmitField('Sign Up',
        render_kw={"class": "btn-full"}
    )