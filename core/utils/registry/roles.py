from core.models.users import Role, db

def register_role(name: str, description: str = None):
    exists = Role.query.filter_by(name=name).first()

    if exists:
        return False

    role = Role(name=name, description=description)
    db.session.add(role)
    db.session.commit()
    return True