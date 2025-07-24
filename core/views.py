from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user # type: ignore
from .models import User
from .extensions import db
from .forms import * 
import uuid, os
from werkzeug.utils import secure_filename

core = Blueprint('core', __name__, static_folder='static', template_folder='templates')

@core.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('core.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('core.dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    return render_template('auth/login.html', form=form)

@core.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('core.dashboard'))
    
    form = RegisterForm()

    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            form.email.errors.append('Email already exists.')
        
        if form.password.data != form.retype_password.data:
            form.retype_password.errors.append('Passwords do not match.')
        
        if User.query.filter_by(username=form.username.data).first():
            form.username.errors.append('Username already exists.')
        
        if not form.errors:
            new_user = User(
                username=form.username.data,
                email=form.email.data,
            )
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('core.dashboard'))
        
    return render_template('auth/register.html', form=form)

@core.route('/profile', methods = ['GET', 'POST'])
@login_required
def profile():

    edit_name_form = EditNameForm()
    edit_profile_form = EditProfileForm()

    if edit_name_form.validate_on_submit():
        current_user.firstname = edit_name_form.firstname.data
        current_user.lastname = edit_name_form.lastname.data
        current_user.username = edit_name_form.username.data
        current_user.email = edit_name_form.email.data
        db.session.commit()
        flash('Profile updated successfully.', 'global-success')
        
    if edit_profile_form.validate_on_submit():
        if edit_profile_form.profile_image.data:
            image_file = edit_profile_form.profile_image.data

            ext = os.path.splitext(secure_filename(image_file.filename))[1]
            unique_filename = f"{uuid.uuid4().hex}{ext}"
            save_path = os.path.join(core.static_folder, 'images', 'profiles', unique_filename)

            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            image_file.save(save_path)

            current_user.profile_image = unique_filename
            db.session.commit()

            flash('Profile image updated successfully.', 'global-success')
        else:
            flash('No image selected.', 'global-error')
    return render_template('dashboard/profile.html', user=current_user, edit_name_form = edit_name_form, edit_profile_form = edit_profile_form)

@core.route('/extensions')
@login_required
def extensions():
    return render_template('dashboard/extensions.html', user=current_user)

@core.route('/users')
@login_required
def users():
    users = User.query.all()
        
    return render_template('dashboard/users.html', user=current_user, users = users)

@core.route('/users/manage/<string:user_uid>', methods=['GET', 'POST'])
@login_required
def manage_user(user_uid):
    
    if current_user.uid == user_uid:
        flash('You cannot manage your own account in this page. Please use the profile page', 'global-error')
        return redirect(url_for('core.users'))
    
    password_form = ManageUserPasswordForm()
    name_form = EditNameForm()
    role_form = ManageUserRoleForm()
    edit_profile_form = EditProfileForm()

    role_form.role.choices = [(role.name, role.name) for role in Role.query.all()]
    selected_user = User.query.filter_by(uid=user_uid).first_or_404()

    if edit_profile_form.validate_on_submit():
        if edit_profile_form.profile_image.data:

            if selected_user.profile_image != 'default-avatar.jpg':
                old_image_path = os.path.join(core.static_folder, 'images', 'profiles', selected_user.profile_image)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)

            image_file = edit_profile_form.profile_image.data

            ext = os.path.splitext(secure_filename(image_file.filename))[1]
            unique_filename = f"{uuid.uuid4().hex}{ext}"
            save_path = os.path.join(core.static_folder, 'images', 'profiles', unique_filename)

            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            image_file.save(save_path)

            selected_user.profile_image = unique_filename
            db.session.commit()

            flash('Profile image updated successfully.', 'global-success')
        else:
            flash('No image selected.', 'global-error')

    if role_form.validate_on_submit():
        selected_user.role = role_form.role.data
        db.session.commit()
        flash('User role updated successfully.', 'global-success')        

    if name_form.validate_on_submit():
        selected_user.firstname = name_form.firstname.data
        selected_user.lastname = name_form.lastname.data
        selected_user.username = name_form.username.data
        selected_user.email = name_form.email.data
        db.session.commit()
        flash('User details updated successfully.', 'global-success')

    if password_form.validate_on_submit():
        selected_user.set_password(password_form.new_password.data)
        db.session.commit()
        flash('User password updated successfully.', 'global-success')

    return render_template('dashboard/manage_user.html', user=current_user, name_form=name_form, selected_user=selected_user, password_form=password_form, role_form=role_form, edit_profile_form=edit_profile_form)

@core.route('/users/create', methods=['GET', 'POST'])
@login_required
def create_user():
    form = CreateUserForm()

    form.role.choices = [(role.name, role.name) for role in Role.query.all()]

    if form.validate_on_submit():
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            role=form.role.data
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('User created successfully.', 'global-success')
        return redirect(url_for('core.users'))

    return render_template('dashboard/create_user.html', user=current_user, form=form)

@core.route('/home')
@login_required
def dashboard():
    return render_template('dashboard/home.html', user=current_user)

@core.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = create_settings_form()

    if form.validate_on_submit():
        for field in form:
            setting = Setting.query.filter_by(key=field.name).first()
            if setting:
                setting.value = field.data
                db.session.commit()
        flash('Settings updated successfully.', 'global-success')
    return render_template('dashboard/settings.html', user=current_user, form = form)

@core.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('core.login'))

