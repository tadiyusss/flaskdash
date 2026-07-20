from core.commands import DEFAULT_COMMANDS
from core.utils.registry.commands import register_command

def register_default_commands():
    for command in DEFAULT_COMMANDS:
        register_command(command)