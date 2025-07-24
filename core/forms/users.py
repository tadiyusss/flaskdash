from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length
from core.styles import Style

style = Style()

class CreateUserForm(FlaskForm):
    username = StringField('Username', 
        validators=[DataRequired(), Length(min=2, max=20)], 
        render_kw={"class": style.text_input}
    )
    email = StringField('Email', 
        validators=[DataRequired(), Email()],
        render_kw={"class": style.text_input}
    )

    firstname = StringField('First Name', 
        validators=[DataRequired(), Length(min=2, max=32)],
        render_kw={"class": style.text_input}
    )

    lastname = StringField('Last Name',
        validators=[DataRequired(), Length(min=2, max=32)],
        render_kw={"class": style.text_input}
    )

    password = PasswordField('Password', 
        validators=[DataRequired(), Length(min=6)],
        render_kw={"class": style.text_input}
    )

    role = SelectField('Role',
        validators=[DataRequired()],
        render_kw={"class": style.text_input}
    )

class ManageUserRoleForm(FlaskForm):
    role = SelectField('Role',
        validators=[DataRequired()],
        render_kw={"class": style.text_input}
    )

    submit = SubmitField('Change Role',
        render_kw={"class": style.button}
    )

class ManageUserPasswordForm(FlaskForm):
    new_password = PasswordField('New Password',
        validators=[DataRequired(), Length(min=6)],
        render_kw={"class": style.text_input}
    )
    submit = SubmitField('Change Password',
        render_kw={"class": style.button}
    )