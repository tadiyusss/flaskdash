from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    email = EmailField('Email Address', 
        validators=[DataRequired(message="Email is required"), Email(message="Enter a valid email")],
        render_kw={
            "class": "w-full pl-10 pr-4 py-2.5 border border-blue-600/30 rounded-lg text-blue-800 text-sm placeholder:text-blue-800/25 bg-white focus:border-blue-600 focus:ring-2 focus:ring-blue-600/10 transition",
            "placeholder": "you@company.com"
        },
    )
    password = PasswordField('Password', 
        validators=[DataRequired(message="Password is required")],
        render_kw={
            "class": "w-full pl-10 pr-4 py-2.5 border border-blue-600/30 rounded-lg text-blue-800 text-sm placeholder:text-blue-800/25 bg-white focus:border-blue-600 focus:ring-2 focus:ring-blue-600/10 transition",
            "placeholder": "Your password",
            ":type": "show ? 'text' : 'password'"
        }
    )

class RegisterForm(FlaskForm):
    username = StringField('Username', 
        validators=[DataRequired(message="Username is required"), Length(min=2, max=20)], 
        render_kw={"class": "text-input"}
    )
    email = StringField('Email', 
        validators=[DataRequired(message="Email is required"), Email(message="Enter a valid email")],
        render_kw={"class": "text-input"}
    )
    password = PasswordField('Password', 
        validators=[DataRequired(message="Password is required"), Length(min=6)],
        render_kw={"class": "text-input"}
    )
    retype_password = PasswordField('Confirm Password', 
        validators=[DataRequired(message="Please confirm your password"), Length(min=6)],
        render_kw={"class": "text-input"}
    )
    submit = SubmitField('Sign Up',
        render_kw={"class": "btn-full"}
    )