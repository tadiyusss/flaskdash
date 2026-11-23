from flask_mail import Message
from core.extensions import mail
from pathlib import Path
from flask import render_template


DEFAULT_TEMPLATE_FOLDER_PATH = Path(__file__).parent.parent / "templates"

def send_email_template(template_name: str, subject: str, recipients: list[str], template_folder_path: Path = DEFAULT_TEMPLATE_FOLDER_PATH, **kwargs):
    if not template_folder_path.exists():
        raise FileNotFoundError(f"Template folder path '{template_folder_path}' does not exist.")

    context = kwargs
    template_content = render_template(template_name, **context)
    message = Message(subject, recipients=recipients)
    message.html = template_content

    text_template = str(Path(template_name).with_suffix(".txt"))
    if (template_folder_path / text_template).is_file():
        message.body = render_template(text_template, **context)

    mail.send(message)
