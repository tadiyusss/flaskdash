from flask_login import login_required, login_user, logout_user, current_user
from flask import Blueprint, render_template, redirect, url_for, flash, request
from core.forms.auth import LoginForm, RegisterForm, ForgotPasswordForm, ResetPasswordForm
from core.extensions import db
from core.models.users import User, UserRole, Role
from flask import g
from core.models.users import LoginHistory
from core.utils.email import send_password_reset_email
from core.utils.tokens import verify_reset_token

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
        else:
            if form.errors:
                for field, errors in form.errors.items():
                    for error in errors:
                        flash(f"{getattr(form, field).label.text}: {error}", 'error')
        return render_template('auth/login.html', form=form)

    @core.route('/register', methods=['GET', 'POST'])
    def register():
        if g.settings['allow_registration'] == '0':
            flash('User registration is disabled.', 'error')
            return redirect(url_for('core.login'))

        if current_user.is_authenticated:
            return redirect(url_for('core.dashboard'))
        
        form = RegisterForm()

        if g.settings['allow_first_name_last_name'] == '0':
            del form.firstname
            del form.lastname

        if form.validate_on_submit():
            if User.query.filter_by(email=form.email.data).first():
                form.email.errors.append('Email already exists.')
            
            if form.password.data != form.retype_password.data:
                form.retype_password.errors.append('Passwords do not match.')
            
            if User.query.filter_by(username=form.username.data).first():
                form.username.errors.append('Username already exists.')

            if not form.errors:

                firstname = form.firstname.data if g.settings['allow_first_name_last_name'] == '1' else None
                lastname = form.lastname.data if g.settings['allow_first_name_last_name'] == '1' else None

                new_user = User(
                    firstname=firstname,
                    lastname=lastname,
                    username=form.username.data,
                    email=form.email.data
                )
                new_user.set_password(form.password.data)
                db.session.add(new_user)
                db.session.commit()

                default_role = Role.query.filter_by(name=g.settings['default_user_role']).first()

                if default_role:
                    user_role = UserRole(user_id=new_user.id, role_id=default_role.id)
                    db.session.add(user_role)
                    db.session.commit()

                login_user(new_user)
                return redirect(url_for('core.dashboard'))
            
        return render_template('auth/register.html', form=form)

    @core.route('/forgot-password', methods=['GET', 'POST'])
    def forgot_password():
        form = ForgotPasswordForm()

        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                try:
                    send_password_reset_email(user)
                except Exception as e:
                    flash('Failed to send email. Please try again later.', 'error')
                    return redirect(url_for('core.forgot_password'))            
            flash('Password reset instructions have been sent to your email.', 'success')        
        return render_template('auth/forgot-password.html', form=form)

    @core.route('/reset-password/<token>', methods=['GET', 'POST'])
    def reset_password(token):
        user = verify_reset_token(token)
        form = ResetPasswordForm()
        if not user:
            flash('Invalid or expired token.', 'error')
            return redirect(url_for('core.forgot_password'))
        
        if form.validate_on_submit():
            if form.password.data != form.retype_password.data:
                form.retype_password.errors.append('Passwords do not match.')
            else:

                if user:
                    user.set_password(form.password.data)
                    flash('Your password has been reset. You can now log in.', 'success')
                    return redirect(url_for('core.login'))
                else:
                    flash('User not found.', 'error')
                    return redirect(url_for('core.forgot_password'))
        return render_template('auth/reset-password.html', token=token, form=form)

    @core.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('core.login'))