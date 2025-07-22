from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user # type: ignore
from .models import User
from .extensions import db
from .forms import * 

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

    if edit_name_form.validate_on_submit():
        current_user.firstname = edit_name_form.firstname.data
        current_user.lastname = edit_name_form.lastname.data
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        
    return render_template('dashboard/profile.html', user=current_user, edit_name_form = edit_name_form)

@core.route('/extensions')
@login_required
def extensions():
    return render_template('dashboard/extensions.html', user=current_user)

@core.route('/users')
@login_required
def users():
    return render_template('dashboard/users.html', user=current_user)

@core.route('/home')
@login_required
def dashboard():
    return render_template('dashboard/home.html', user=current_user)

@core.route('/settings')
@login_required
def settings():
    return render_template('dashboard/settings.html', user=current_user)

@core.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('core.login'))

