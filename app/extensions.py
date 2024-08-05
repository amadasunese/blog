from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
migrate = Migrate()
# login = LoginManager()
# login_manager.login_view = 'main.login'
# login.login_view = 'main.login'
bcrypt = Bcrypt()
# login_manager.login_message_category = 'info'
csrf = CSRFProtect