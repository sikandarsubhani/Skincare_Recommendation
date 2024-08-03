from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'main_bp.login'
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '70113185'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///skin.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    from .models import User  # Import models here after app and db initialization

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        from .routes import main_bp
        app.register_blueprint(main_bp)

        from .admin_routes import admin_bp
        app.register_blueprint(admin_bp, url_prefix='/admin')
        db.create_all()

    return app
