from functools import wraps
from flask_login import current_user
from flask import abort


def role_required(role):
    """
    Decorator to check if the current user has the required role.
    
    :usage: @role_required(role_name)
    :param role: The role required to access the decorated view.
    :raises: 403 Forbidden if the user does not have the required role or is not authenticated.
    
    """

    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            
            if not current_user.is_authenticated:
                abort(403)
            if not current_user.has_role(role):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return wrapper