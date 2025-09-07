from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, HiddenField
from wtforms.validators import DataRequired, Email, Length, ValidationError
from .validators import validate_my_email_unique, validate_my_username_unique
from core.styles import Style
from flask_wtf.file import FileField, FileAllowed, FileRequired
from . import ALLOWED_IMAGE_EXTENSIONS
from wtforms.validators import Regexp

style = Style()

class EditNameForm(FlaskForm):
    username = StringField('Username',
        validators=[DataRequired("Username is required."), Length(min=2, max=20), validate_my_username_unique],
        render_kw={"class": style.text_input}
    )

    email = EmailField('Email',
        validators=[DataRequired("Email is required."), Email(), validate_my_email_unique],
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

class EditProfileForm(FlaskForm):
    profile_image = FileField('Profile Image',
        validators=[FileAllowed(ALLOWED_IMAGE_EXTENSIONS, 'Invalid file extension.'), FileRequired('File was empty!')],
        render_kw={"class": "hidden", "x-on:change": "imagePreview()", "accept": "image/*"}
    )
    submit = SubmitField('Change Image',
        render_kw={"class": style.button},
    )

class EditPasswordForm(FlaskForm):
    current_password = StringField('Current Password',
        validators=[DataRequired("Current password is required.")],
        render_kw={"class": style.text_input, "type": "password"}
    )

    new_password = StringField('New Password',
        validators=[DataRequired("New password is required."), Length(min=6, message="Password must be at least 6 characters long.")],
        render_kw={"class": style.text_input, "type": "password"}
    )

    submit = SubmitField('Change Password',
        render_kw={"class": style.button}
    )