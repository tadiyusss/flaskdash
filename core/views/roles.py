from core.models.users import Role
from core.forms.users import CreateRoleForm
from flask_login import login_required, current_user
from flask import render_template, redirect, url_for, flash
from core.extensions import db
from core.utils.decorators import role_required
from core.defaults import DEFAULT_ROLES

def generate_blueprint(core):
    @core.route('/roles', methods=['GET', 'POST'])
    @role_required('Administrator')
    @login_required
    def roles():
        roles = Role.query.all()
        form = CreateRoleForm()
        default_roles = [role['name'] for role in DEFAULT_ROLES]
        if form.validate_on_submit():
            new_role = Role(
                name=form.name.data,
                description=form.description.data
            )
            db.session.add(new_role)
            db.session.commit()
            flash('Role created successfully.', 'global-success')
            return redirect(url_for('core.roles'))
        else:
            for error in form.errors.values():
                flash(error[0], 'global-error')

        return render_template('dashboard/roles.html', user=current_user, roles=roles, form=form, default_roles=default_roles)
    
    @core.route('/roles/<string:role_uid>/delete')
    @role_required('Administrator')
    @login_required
    def delete_role(role_uid):
        role = Role.query.filter_by(uid=role_uid).first_or_404()
        if role.name in [r['name'] for r in DEFAULT_ROLES]:
            flash('You cannot delete a default role.', 'global-error')
            return redirect(url_for('core.roles'))

        db.session.delete(role)
        db.session.commit()
        flash('Role deleted successfully.', 'global-success')
        return redirect(url_for('core.roles'))