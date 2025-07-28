from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from core.extensions import db
from core.utils.decorators import role_required
from core.forms.files import FileUploadForm
from core.models.files import FileUpload
import os
from hashlib import sha256
import uuid

def generate_routes(core):

    @core.route('/files/<string:uid>/delete', methods=['GET'])
    @role_required('Administrator')
    @login_required
    def delete_file(uid):
        file_upload = FileUpload.query.filter_by(uid=uid).first_or_404()
        # get all rows that have the same filehash
        similar_uploads = FileUpload.query.filter_by(file_hash=file_upload.file_hash).all()
        if len(similar_uploads) > 1:
            # if there are other uploads with the same hash, just delete this one
            db.session.delete(file_upload)
            db.session.commit()
        else:
            # if this is the only upload with this hash, delete the file from the filesystem
            upload_folder = os.path.join(core.static_folder, 'uploads')
            file_path = os.path.join(upload_folder, file_upload.absolute_filename)
            if os.path.exists(file_path):
                os.remove(file_path)
            db.session.delete(file_upload)
            db.session.commit()
        flash('File deleted successfully!', 'global-success')
        return redirect(url_for('core.files'))

    @core.route('/files', methods=['GET', 'POST'])
    @role_required('Administrator')
    @login_required
    def files():
        form = FileUploadForm()
        
        if form.validate_on_submit():
            # check if folder /static/uploads exists, if not create it
            upload_folder = os.path.join(core.static_folder, 'uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            # get the file's hash
            file = form.file.data
            file_hash = sha256(file.read()).hexdigest()
            file.seek(0) # reset file pointer after reading for hash
            # check if file with the same hash already exists
            existing_file = FileUpload.query.filter_by(file_hash=file_hash).first()
            if existing_file:
                file_model = FileUpload(
                    uploaded_filename=file.filename,
                    absolute_filename=existing_file.absolute_filename,
                    file_hash=file_hash
                )
                db.session.add(file_model)
                db.session.commit()
            else:
                # save the file
                filename = f"{uuid.uuid4().hex}_{file.filename}"
                absolute_filename = filename
                file_path = os.path.join(upload_folder, absolute_filename)
                file.save(file_path)

                # create a new FileUpload record
                file_model = FileUpload(
                    uploaded_filename=file.filename,
                    absolute_filename=absolute_filename,
                    file_hash=file_hash
                )
                db.session.add(file_model)
                db.session.commit()
            flash('File uploaded successfully!', 'global-success')
            
        files_uploaded = FileUpload.query.order_by(FileUpload.upload_date.desc()).all()
        return render_template('dashboard/files.html', user=current_user, form = form, files_uploaded = files_uploaded)