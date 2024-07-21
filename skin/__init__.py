from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import login_user,logout_user,login_required
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from tensorflow.keras.metrics import AUC




app = Flask(__name__)
app.config['SECRET_KEY'] = '70113185'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///skin.db'
db = SQLAlchemy()
db.init_app(app)
bcrypt=Bcrypt(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

dependencies = {
    'auc_roc': AUC
}

from skin import routes