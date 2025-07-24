from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, IntegerField, EmailField, URLField, FileField, SelectField
from wtforms.validators import DataRequired, Email, Length
from .styles import Style
from .models import Setting, Role
from flask import current_app

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

class ManageUserNameForm(FlaskForm):

    username = StringField('Username',
        validators=[DataRequired(), Length(min=2, max=20)],
        render_kw={"class": style.text_input}
    )

    email = EmailField('Email',
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

    submit = SubmitField('Save Changes',
        render_kw={"class": style.button}
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
        render_kw={"class": style.button}
    )

class EditNameForm(FlaskForm):
    username = StringField('Username',
        validators=[DataRequired(), Length(min=2, max=20)],
        render_kw={"class": style.text_input}
    )

    email = EmailField('Email',
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

    submit = SubmitField('Save Changes',
        render_kw={"class": style.button}
    )
    
def create_settings_form():
    class DynamicSettingsForm(FlaskForm):
        pass

    settings = Setting.query.all()
    for setting in settings:
        field_type = setting.type.value
        if field_type == 'text':
            field = StringField(setting.name,
                default=setting.value,
                description=setting.description,
                render_kw={"class": style.text_input}
            )
        elif field_type == 'textarea':
            field = TextAreaField(setting.name,
                default=setting.value,
                description=setting.description,
                render_kw={"class": style.textarea}
            )
        elif field_type =='number':
            field = IntegerField(setting.name,
                default=setting.value,
                description=setting.description,
                render_kw={"class": style.text_input}
            )
        elif field_type == 'email':
            field = EmailField(setting.name,
                default=setting.value,
                description=setting.description,
                render_kw={"class": style.text_input}
            )
        elif field_type == 'url':
            field = URLField(setting.name,
                default=setting.value,
                description=setting.description,
                render_kw={"class": style.text_input}
            )
        elif field_type == 'datetime':
            field = StringField(setting.name,
                default=setting.value,
                description=setting.description,
                render_kw={"class": style.text_input}
            )
        else:
            continue
        setattr(DynamicSettingsForm, setting.key, field)
    return DynamicSettingsForm()