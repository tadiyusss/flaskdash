from flask import current_app

def register_command(command):
    """
    Register a new command in the system.
    :param command: The command to register.
    """
    current_app.logger.debug(f"Registering command: {command.name}")
    current_app.cli.add_command(command)