import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

app = Flask(__name__)


database_url = os.getenv('DATABASE_URL_INTERNAL')

if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///dataflexi.db'


app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'secret')
app.config['UPLOAD_FOLDER'] = 'static/posts_photos'

database = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'homepage'

from appflexi import routes