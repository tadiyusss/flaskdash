from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, Length
from core.styles import Style
from flask_wtf.file import FileField, FileAllowed, FileRequired
from . import ALLOWED_IMAGE_EXTENSIONS

style = Style()

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

class EditProfileForm(FlaskForm):
    profile_image = FileField('Profile Image',
        validators=[FileAllowed(ALLOWED_IMAGE_EXTENSIONS, 'Invalid file extension.'), FileRequired('File was empty!')],
        render_kw={"class": "hidden", "x-on:change": "imagePreview()", "accept": "image/*"}
    )
    submit = SubmitField('Change Image',
        render_kw={"class": style.button},
    )

class EditProfileForm(FlaskForm):
    profile_image = FileField('Profile Image',
        validators=[FileAllowed(ALLOWED_IMAGE_EXTENSIONS, 'Invalid file extension.'), FileRequired('File was empty!')],
        render_kw={"class": "hidden", "x-on:change": "imagePreview()", "accept": "image/*"}
    )
    submit = SubmitField('Change Image',
        render_kw={"class": style.button},
    )