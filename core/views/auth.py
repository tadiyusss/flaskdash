from flask_login import login_required, login_user, logout_user, current_user
from flask import Blueprint, render_template, redirect, url_for, flash, request
from core.forms.auth import LoginForm, RegisterForm
from core.extensions import db
from core.models.users import User 
from flask import g
from core.models.users import LoginHistory


def generate_routes(core):

    @core.route('/', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('core.dashboard'))
        
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                # Record login history
                login_history = LoginHistory(user_id=user.id, ip_address=request.remote_addr)
                db.session.add(login_history)
                db.session.commit()
                return redirect(url_for('core.dashboard'))
            else:
                flash('Invalid email or password.', 'error')
        return render_template('auth/login.html', form=form)

    @core.route('/register', methods=['GET', 'POST'])
    def register():
        if g.settings['allow_registration'] == '0':
            flash('User registration is disabled.', 'error')
            return redirect(url_for('core.login'))

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
                    role=g.settings['default_user_role']
                )
                new_user.set_password(form.password.data)
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                return redirect(url_for('core.dashboard'))
            
        return render_template('auth/register.html', form=form)

    @core.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('core.login'))