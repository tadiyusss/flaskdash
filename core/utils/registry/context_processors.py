
from flask import current_app

_registered_context_processors = []

def register_context_processor(processor):
    """
    Register a new context processor in the system.
    :param processor: The context processor function to register.
    """
    current_app.logger.info(f"Registering context processor: {processor.__name__}")
    _registered_context_processors.append(processor)
    current_app.context_processor(processor)

def get_registered_context_processors():
    return _registered_context_processors