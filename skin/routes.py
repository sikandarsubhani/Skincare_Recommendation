from flask import Blueprint, render_template, redirect, url_for, flash, request
from . import db, bcrypt
from .forms import RegisterForm, LoginForm
from .models import User
from flask_login import login_user, logout_user, login_required, current_user
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.metrics import AUC
import numpy as np

main_bp = Blueprint('main_bp', __name__)

dependencies = {'auc_roc': AUC}
verbose_name = {
    0: 'Actinic keratoses and intraepithelial carcinomae',
    1: 'Basal cell carcinoma',
    2: 'Benign keratosis-like lesions',
    3: 'Dermatofibroma',
    4: 'Melanocytic nevi',
    5: 'Pyogenic granulomas and hemorrhage',
    6: 'Melanoma',
    7: 'Hives',
    8: 'Scabies',
    9: 'Bullous Pemphigoid',
    10: 'Acne/Rosacea',
    11: 'Vascular Tumor',
    12: 'Vasculitis',
    13: 'Pigmentation Disorder',
    14: 'STDs - Herpes/AIDS'
}

model = load_model('skin/model/dermnet_m2.h5', custom_objects=dependencies)

def predict_label(img_path):
    test_image = image.load_img(img_path, target_size=(28, 28))
    test_image = image.img_to_array(test_image) / 255.0
    test_image = np.expand_dims(test_image, axis=0)

    predict_x = model.predict(test_image)
    classes_x = np.argmax(predict_x, axis=1)

    return verbose_name[classes_x[0]]

@main_bp.route("/")
@main_bp.route("/first")
def first():
    return render_template('first.html')

@main_bp.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data, email=form.email.data, password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('main_bp.login'))
    return render_template('register.html', title='Register', form=form)

@main_bp.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('main_bp.index'))
        else:
            flash('Username or password is incorrect', category='danger')
    return render_template('login.html', form=form)

@main_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", category='info')
    return redirect(url_for('main_bp.login'))

@main_bp.route("/index", methods=['GET', 'POST'])
@login_required
def index():
    return render_template("index.html")

@main_bp.route("/submit", methods=['GET', 'POST'])
@login_required
def get_output():
    if request.method == 'POST':
        img = request.files['my_image']
        img_path = "static/tests/" + img.filename
        img.save(img_path)

        predict_result = predict_label(img_path)
        recommendation_is = "Cannot recommend"

        if "Basal cell" in predict_result:
            recommendation_is = "Electrodesiccation and curettage (EDC)"
        elif "Actinic" in predict_result:
            recommendation_is = "Liquid Nitrogen Cryosurgery"
        elif "keratosis" in predict_result:
            recommendation_is = "Phototherapy"
        elif "Dermatofibroma" in predict_result:
            recommendation_is = "Surgical shaving of top"
        elif "nevi" in predict_result:
            recommendation_is = "Surgical removal for cosmetic consideration"
        elif "Melanoma" in predict_result:
            recommendation_is = "Surgery"
        elif "hemorrhage" in predict_result:
            recommendation_is = "Electrocautery"
        elif "pyogenic granulomas" in predict_result:
            recommendation_is = "Laser therapy"
        elif "acne" in predict_result:
            recommendation_is = "Topical treatments"
        elif "Vascular Tumor" in predict_result:
            recommendation_is = "Surgical removal"
        elif "Vasculitis" in predict_result:
            recommendation_is = "Corticosteroids"
        elif "Pigmentation Disorder" in predict_result:
            recommendation_is = "Topical treatments"
        elif "STDs" in predict_result:
            recommendation_is = "Antiviral medication"

    return render_template("prediction.html", prediction=predict_result, img_path=img_path, recommendation_result=recommendation_is)

@main_bp.route("/Graph")
def Graph():
    return render_template('Graph.html')

@main_bp.route("/chart")
def chart():
    return render_template('chart.html')
