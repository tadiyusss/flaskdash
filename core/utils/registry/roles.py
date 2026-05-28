from core.models.users import Role as RoleModel
from core import db
from core.utils.roles import Role

def register_role(role: Role):
    exists = RoleModel.query.filter_by(name=role.name).first()

    if exists:
        return False

    role = RoleModel(name=role.name, description=role.description)
    db.session.add(role)
    db.session.commit()
    return True