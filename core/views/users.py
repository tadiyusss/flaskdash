from flask_login import login_required, login_user, logout_user, current_user
from flask import render_template, redirect, url_for, flash, request
from core.models import User, Role
from core.forms.users import CreateUserForm, ManageUserPasswordForm, ManageUserRoleForm
from core.forms.profile import EditNameForm, EditProfileForm
from core.extensions import db
import os
import uuid
from werkzeug.utils import secure_filename
from core.utils.decorators import role_required

def generate_blueprint(core):
    
    @core.route('/users/create', methods=['GET', 'POST'])
    @role_required('Administrator')
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

    @core.route('/users')
    @role_required('Administrator')
    @login_required
    def users():
        users = User.query.all()
        return render_template('dashboard/users.html', user=current_user, users = users)
    

    @core.route('/users/manage/<string:user_uid>/edit/name', methods=['GET', 'POST'])
    @role_required('Administrator')
    @login_required
    def edit_user_name(user_uid):
        selected_user = User.query.filter_by(uid=user_uid).first_or_404()
        name_form = EditNameForm(obj=selected_user)

        if not name_form.validate_on_submit():
            for error in name_form.errors.values():
                flash(error[0], 'global-error')
            return redirect(url_for('core.manage_user', user_uid=user_uid))

        selected_user.firstname = name_form.firstname.data
        selected_user.lastname = name_form.lastname.data
        selected_user.username = name_form.username.data
        selected_user.email = name_form.email.data
        db.session.commit()
        flash('User details updated successfully.', 'global-success')
        return redirect(url_for('core.manage_user', user_uid=user_uid))

    @core.route('/users/manage/<string:user_uid>/edit/password', methods=['GET', 'POST'])
    @role_required('Administrator')
    @login_required
    def edit_user_password(user_uid):
        selected_user = User.query.filter_by(uid=user_uid).first_or_404()
        password_form = ManageUserPasswordForm()

        if not password_form.validate_on_submit():
            for error in password_form.errors.values():
                flash(error[0], 'global-error')
            return redirect(url_for('core.manage_user', user_uid=user_uid))

        selected_user.set_password(password_form.new_password.data)
        db.session.commit()
        flash('User password updated successfully.', 'global-success')
        return redirect(url_for('core.manage_user', user_uid=user_uid))

    @core.route('/users/manage/<string:user_uid>/edit/role', methods=['POST'])
    @role_required('Administrator')
    @login_required
    def edit_user_role(user_uid):
        selected_user = User.query.filter_by(uid=user_uid).first_or_404()
        role_form = ManageUserRoleForm()
        role_form.role.choices = [(role.name, role.name) for role in Role.query.all()]

        if not role_form.validate_on_submit():
            for error in role_form.errors.values():
                flash(error[0], 'global-error')
            return redirect(url_for('core.manage_user', user_uid=user_uid))

        selected_user.role = role_form.role.data
        db.session.commit()
        flash('User role updated successfully.', 'global-success')
        return redirect(url_for('core.manage_user', user_uid=user_uid))

    @core.route('/users/manage/<string:user_uid>/edit/picture', methods=['GET', 'POST'])
    @role_required('Administrator')
    @login_required
    def edit_user_picture(user_uid):
        selected_user = User.query.filter_by(uid=user_uid).first_or_404()
        edit_profile_form = EditProfileForm(obj=selected_user)

        if not edit_profile_form.validate_on_submit():
            for error in edit_profile_form.errors.values():
                flash(error[0], 'global-error')
            return redirect(url_for('core.manage_user', user_uid=user_uid))
        
        if not edit_profile_form.profile_image.data:
            flash('No image selected.', 'global-error')
            return redirect(url_for('core.manage_user', user_uid=user_uid))

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
        return redirect(url_for('core.manage_user', user_uid=user_uid))

    @core.route('/users/manage/<string:user_uid>', methods=['GET', 'POST'])
    @role_required('Administrator')
    @login_required
    def manage_user(user_uid):
        
        if current_user.uid == user_uid:
            flash('You cannot manage your own account in this page. Please use the profile page', 'global-error')
            return redirect(url_for('core.users'))
        
        password_form = ManageUserPasswordForm()
        name_form = EditNameForm()
        role_form = ManageUserRoleForm()
        edit_profile_form = EditProfileForm()

        selected_user = User.query.filter_by(uid=user_uid).first_or_404()
        role_form.role.choices = [(role.name, role.name) for role in Role.query.all()]
        role_form.role.data = selected_user.role

        return render_template('dashboard/manage_user.html', user=current_user, name_form=name_form, selected_user=selected_user, password_form=password_form, role_form=role_form, edit_profile_form=edit_profile_form)