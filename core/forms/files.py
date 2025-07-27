from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import ValidationError
from flask_wtf.file import FileRequired

class FileUploadForm(FlaskForm):
    file = FileField('File', validators=[FileRequired()])
    submit = SubmitField('Upload')
    
    def validate_file(self, field):
        if not field.data:
            raise ValidationError('No file selected.')
        if field.data.filename == '':
            raise ValidationError('No file selected.')