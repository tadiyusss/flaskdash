from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, EmailField, TextAreaField, BooleanField
from core.forms.validators import validate_username_unique, validate_email_unique, validate_role_name_unique, validate_password_length, validate_password_uppercase_letter, validate_password_lowercase_letter, validate_password_digit, validate_my_username_unique, validate_my_email_unique
from wtforms.validators import DataRequired, Email, Length, Regexp
from core.models.users import Role, User

class CreateRoleForm(FlaskForm):
    name = StringField('Role Name',
        validators=[DataRequired("Role name is required."), Length(min=2, max=50), validate_role_name_unique],
        render_kw={"class": "text-input"}
    )

    description = TextAreaField('Description',
        validators=[DataRequired("Description is required."), Length(max=200)],
        render_kw={"class": "text-input", "rows": 3}
    )

    submit = SubmitField('Create Role',
        render_kw={"class": "btn"}
    )

class CreateUserForm(FlaskForm):
    username = StringField('Username', 
        validators=[DataRequired(), Length(min=2, max=20), validate_username_unique], 
        render_kw={"class": "text-input"}
    )
    email = StringField('Email', 
        validators=[DataRequired(), Email(), validate_email_unique],
        render_kw={"class": "text-input"}
    )

    firstname = StringField('First Name', 
        validators=[DataRequired(), Length(min=2, max=32), Regexp(r'^[a-zA-Z]+$', message="First name must contain only letters.")],
        render_kw={"class": "text-input"}
    )

    lastname = StringField('Last Name',
        validators=[DataRequired(), Length(min=2, max=32), Regexp(r'^[a-zA-Z]+$', message="Last name must contain only letters.")],
        render_kw={"class": "text-input"}
    )

    password = PasswordField('Password', 
        validators=[DataRequired(), validate_password_length, validate_password_uppercase_letter, validate_password_lowercase_letter, validate_password_digit],
        render_kw={"class": "text-input"},
    )

    role = SelectField('Role',
        validators=[DataRequired()],
        render_kw={"class": "text-input"}
    )

def build_manage_user_role_form(user: User):
    class DynamicManageUserRoleForm(FlaskForm):
        submit = SubmitField('Change Role',
            render_kw={"class": "btn"}
        )

    roles = Role.query.all()
    user_roles = [user_role.role.name for user_role in user.user_roles]
    for role in roles:
        setattr(DynamicManageUserRoleForm, f'role_{role.id}', BooleanField(
                role.name,
                render_kw={"class": "form-checkbox"},
                description=role.description,
                default=role.name in user_roles
            )
        )
    
    return DynamicManageUserRoleForm()

class ManageUserPasswordForm(FlaskForm):
    new_password = PasswordField('New Password',
        validators=[DataRequired(), Length(min=6)],
        render_kw={"class": "text-input"}
    )
    submit = SubmitField('Change Password',
        render_kw={"class": "btn"}
    )

class ManageNameForm(FlaskForm):
    username = StringField('Username',
        validators=[DataRequired("Username is required."), Length(min=2, max=20)],
        render_kw={"class": "text-input"}
    )

    email = EmailField('Email',
        validators=[DataRequired("Email is required."), Email()],
        render_kw={"class": "text-input"}
    )

    firstname = StringField('First Name', 
        validators=[Regexp(r'^[a-zA-Z]+$', message="First name must contain only letters.")],
        render_kw={"class": "text-input"}
    )

    lastname = StringField('Last Name',
        validators=[Regexp(r'^[a-zA-Z]+$', message="Last name must contain only letters.")],
        render_kw={"class": "text-input"}
    )

    submit = SubmitField('Save Changes',
        render_kw={"class": "btn"}
    )