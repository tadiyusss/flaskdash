from core.forms.profile import EditNameForm, EditProfileForm
from flask_login import login_required, current_user
from flask import render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
from core import db
import os
import uuid

def generate_routes(core):

    @login_required
    @core.route('/profile/edit/picture', methods=['POST'])
    def profile_edit_picture():

        edit_profile_form = EditProfileForm()

        if not edit_profile_form.validate_on_submit():
            for error in edit_profile_form.errors.values():
                flash(error[0], 'global-error')
            return redirect(url_for('core.profile'))

        if edit_profile_form.profile_image.data == None:
            flash('No image selected.', 'global-error')

        image_file = edit_profile_form.profile_image.data

        ext = os.path.splitext(secure_filename(image_file.filename))[1]
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        save_path = os.path.join(core.static_folder, 'images', 'profiles', unique_filename)

        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        image_file.save(save_path)

        if current_user.profile_image != 'default-avatar.jpg':
            old_image_path = os.path.join(core.static_folder, 'images', 'profiles', current_user.profile_image)
            if os.path.exists(old_image_path):
                os.remove(old_image_path)

        current_user.profile_image = unique_filename
        db.session.commit()

        flash('Profile image updated successfully.', 'global-success')
        return redirect(url_for('core.profile'))


    @login_required
    @core.route('/profile/edit/name', methods=['POST'])
    def profile_edit_name():
        form = EditNameForm()

        if not form.validate_on_submit():
            for error in form.errors.values():
                flash(error[0], 'global-error')
            return redirect(url_for('core.profile'))

        current_user.firstname = form.firstname.data
        current_user.lastname = form.lastname.data
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Profile name updated successfully.', 'global-success')

        return redirect(url_for('core.profile'))

    @core.route('/profile', methods = ['GET'])
    @login_required
    def profile():

        edit_profile_form = EditProfileForm()
        edit_name_form = EditNameForm()

        return render_template('dashboard/profile.html', user=current_user, edit_name_form = edit_name_form, edit_profile_form = edit_profile_form)