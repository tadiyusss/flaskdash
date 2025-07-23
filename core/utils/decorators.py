from functools import wraps
from flask_login import current_user
from flask import abort


def role_required(role):
    """
    Decorator to check if the current user has the required role.
    """

    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)
            if getattr(current_user, 'roles', None) is None or role != current_user.role:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return wrapper