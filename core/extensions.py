from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate 
from flask_socketio import SocketIO


db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
mail = Mail()
socketio = SocketIO(
    cors_allowed_origins="*",
    async_mode="threading"
)