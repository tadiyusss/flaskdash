from core.models.users import Role as RoleModel
from core import db
from core.utils.roles import Role
from flask import current_app

def register_role(role: Role):
    exists = RoleModel.query.filter_by(name=role.name).first()
    current_app.logger.debug(f"Checking if role '{role.name}' exists in the database.")
    if exists:
        current_app.logger.debug(f"Role '{role.name}' already exists. Skipping registration.")
        return False

    role = RoleModel(name=role.name, description=role.description)
    db.session.add(role)
    db.session.commit()
    current_app.logger.info(f"Registering role: {role.name} - {role.description}")
    return True