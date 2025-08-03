import os
import dotenv

dotenv.load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
        f"sqlite:///{os.path.join(basedir, 'app.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL") or \
        f"sqlite:///{os.path.join(basedir, 'test.db')}"
    TESTING = True
    WTF_CSRF_ENABLED = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    DEBUG = True

class MySQLConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("MYSQL_DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False