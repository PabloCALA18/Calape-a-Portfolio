import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from urllib.parse import quote_plus

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect() 
limiter = Limiter(key_func=get_remote_address)
login_manager.login_view = "login"


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{os.getenv('DB_USER')}:{quote_plus(os.getenv('DB_PASSWORD', ''))}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME')}"
    )
    # Clever Cloud DEV permite solo 5 conexiones: se usan pocas y se reciclan
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True, "pool_recycle": 280,
        "pool_size": 2, "max_overflow": 1,
    }
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app) 
    limiter.init_app(app)                   # protege TODOS los formularios POST
    app.config["MAX_CONTENT_LENGTH"] = 4 * 1024 * 1024   # máx. 4 MB por subida

    # Se importan acá adentro, después de crear db y login_manager,
    # para evitar errores de importación circular.
    from app import models
    from app.routes import registrar_rutas
    registrar_rutas(app)

    return app