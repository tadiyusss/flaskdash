from .users import create_admin, delete_user
from .extensions import create_extension, delete_extension

DEFAULT_COMMANDS = [
    create_admin,
    delete_user,
    create_extension,
    delete_extension
]