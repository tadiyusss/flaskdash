from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, EmailField
from core.forms.validators import validate_username_unique, validate_email_unique
from wtforms.validators import DataRequired, Email, Length, Regexp
from core.styles import Style

style = Style()

class CreateUserForm(FlaskForm):
    username = StringField('Username', 
        validators=[DataRequired(), Length(min=2, max=20), validate_username_unique], 
        render_kw={"class": style.text_input}
    )
    email = StringField('Email', 
        validators=[DataRequired(), Email(), validate_email_unique],
        render_kw={"class": style.text_input}
    )

    firstname = StringField('First Name', 
        validators=[DataRequired(), Length(min=2, max=32), Regexp(r'^[a-zA-Z]+$', message="First name must contain only letters.")],
        render_kw={"class": style.text_input}
    )

    lastname = StringField('Last Name',
        validators=[DataRequired(), Length(min=2, max=32), Regexp(r'^[a-zA-Z]+$', message="Last name must contain only letters.")],
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

class ManageNameForm(FlaskForm):
    username = StringField('Username',
        validators=[DataRequired("Username is required."), Length(min=2, max=20)],
        render_kw={"class": style.text_input}
    )

    email = EmailField('Email',
        validators=[DataRequired("Email is required."), Email()],
        render_kw={"class": style.text_input}
    )

    firstname = StringField('First Name', 
        validators=[Regexp(r'^[a-zA-Z]+$', message="First name must contain only letters.")],
        render_kw={"class": style.text_input}
    )

    lastname = StringField('Last Name',
        validators=[Regexp(r'^[a-zA-Z]+$', message="Last name must contain only letters.")],
        render_kw={"class": style.text_input}
    )

    submit = SubmitField('Save Changes',
        render_kw={"class": style.button}
    )