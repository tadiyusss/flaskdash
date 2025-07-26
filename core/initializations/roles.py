from core.defaults import DEFAULT_ROLES
from core.utils.registry.roles import register_role

def register_default_roles():
    """
    Register default roles.
    """
    for role in DEFAULT_ROLES:
        register_role(**role)
