from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import Config
from app.extensions import db, migrate, bcrypt, csrf
from app.models import User

login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.routes import main
    from app.errors.handlers import errors

    app.register_blueprint(main)
    app.register_blueprint(errors)

    app.static_folder = 'static'
    app.static_url_path = '/static'

    return app
