from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'login'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '70113185'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///skin.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        from .routes import main_bp
        app.register_blueprint(main_bp)
        db.create_all()

    return app
