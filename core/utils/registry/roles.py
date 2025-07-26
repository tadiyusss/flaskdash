from core.models import Role, db

def register_role(name: str, description: str = None):
    exists = Role.query.filter_by(name=name).first()

    if exists:
        print(f"Role '{name}' already exists.")
        return False

    role = Role(name=name, description=description)
    db.session.add(role)
    db.session.commit()
    print(f"Role '{name}' registered successfully.")
    return True