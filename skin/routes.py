from flask import Blueprint, render_template, redirect, url_for, flash, request
from . import db, bcrypt
from .forms import RegisterForm, LoginForm,UpdateProfileForm
from .models import User,Picture,VisitLog
from flask_login import login_user, logout_user, login_required, current_user,login_manager
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.metrics import AUC
import numpy as np
import os
from werkzeug.utils import secure_filename  # Correct import
from datetime import datetime

main_bp = Blueprint('main_bp', __name__)

@main_bp.before_request
def log_user_visit():
    if current_user.is_authenticated:
        visit = VisitLog(user_id=current_user.id, visit_time=datetime.utcnow())
        db.session.add(visit)
        db.session.commit()

UPLOAD_FOLDER = 'skin/static/uploads/'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

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
    if not current_user.is_authenticated:
        return redirect(url_for('main_bp.login'))
    return render_template("index.html")

@main_bp.route("/submit", methods=['POST'])
@login_required
def submit():
    if 'my_image' not in request.files:
        flash('No file part', category='danger')
        return redirect(request.url)

    file = request.files['my_image']

    if file.filename == '':
        flash('No selected file', category='danger')
        return redirect(request.url)

    if file:
        filename = secure_filename(file.filename)
        img_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(img_path)

        # Save the picture in the database
        picture = Picture(filename=filename, user_id=current_user.id)
        db.session.add(picture)
        db.session.commit()

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

        return render_template('prediction.html', prediction=predict_result, img_path=img_path, recommendation_result=recommendation_is)

    return redirect(url_for('main_bp.dashboard'))

@main_bp.route("/Graph")
def Graph():
    return render_template('Graph.html')

@main_bp.route("/chart")
def chart():
    return render_template('chart.html')

@main_bp.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    user = current_user
    form = UpdateProfileForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        db.session.commit()
        flash('Profile updated successfully!', category='success')
        return redirect(url_for('main_bp.dashboard'))
    
    if request.method == 'POST' and 'my_image' in request.files:
        img = request.files['my_image']
        if img:
            filename = secure_filename(img.filename)
            img_path = os.path.join(UPLOAD_FOLDER, filename)
            img.save(img_path)

            picture = Picture(filename=filename, user_id=user.id)
            db.session.add(picture)
            db.session.commit()

            flash('Picture uploaded successfully!', category='success')

    pictures = Picture.query.filter_by(user_id=user.id).all()
    return render_template('dashboard.html', user=user, pictures=pictures,form=form)