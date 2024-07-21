from skin import app,db
from skin.models import User
from skin.forms import RegisterForm,LoginForm
from flask import Flask,render_template,redirect,url_for,flash,get_flashed_messages,request
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import tensorflow as tf
import numpy as np
#from tensorflow import keras
#from keras.layers import Dense
#from keras.models import Sequential, load_model





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
model = load_model('skin/model/best_model.h5')

def predict_label(img_path):
	test_image = image.load_img(img_path, target_size=(28,28))
	test_image = image.img_to_array(test_image)/255.0
	test_image = test_image.reshape(1, 28,28,3)

	predict_x=model.predict(test_image) 
	classes_x=np.argmax(predict_x,axis=1)
	
	return verbose_name[classes_x[0]]


@app.route("/")
@app.route("/first")
def first():
	return render_template('first.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    form=RegisterForm()
    if form.validate_on_submit():
        user_to_create=User(username=form.username.data,email=form.email.data,password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
    
@app.route("/login", methods=['GET', 'POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        attempted_user=User.query.filter_by(username = form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            flash(f'Success! Youre Logged in as: {attempted_user.username}',category='success')
            return redirect(url_for('index'))
        else:
            flash('Username or password is incorrect',category='danger')
    return render_template('login.html',form=form)  
    
@app.route("/index", methods=['GET', 'POST'])
def index():
	return render_template("index.html")


@app.route("/submit", methods=['GET', 'POST'])
def get_output():
    if request.method == 'POST':
        img = request.files['my_image']
        img_path = "skin/static/tests/" + img.filename
        img.save(img_path)

        predict_result = predict_label(img_path)
        recommendation_is = "Cannot recommend"
        link=""
        products=[]

        if "Actinic keratoses and intraepithelial carcinomae" in predict_result:
            recommendation_is = "Liquid Nitrogen Cryosurgery"
            link = "https://www.aad.org/public/diseases/a-z/actinic-keratoses-treatment"
            products = ["CryoPen", "Histofreezer"]

        elif "basal cell carcinoma" in predict_result:
            recommendation_is = "Electrodesiccation and curettage (EDC)"
            link = "https://www.cancer.org/cancer/basal-and-squamous-cell-skin-cancer/treating/basal-cell.html"
            products = ["Curette", "Electrosurgical Unit"]

        elif "benign keratosis-like lesions" in predict_result:
            recommendation_is = "Phototherapy"
            link = "https://www.healthline.com/health/phototherapy"
            products = ["Narrowband UVB Lamp", "Phototherapy Box"]

        elif "dermatofibroma" in predict_result:
            recommendation_is = "Surgical shaving of top"
            link = "https://www.aad.org/public/diseases/a-z/dermatofibroma-treatment"
            products = ["Dermablade", "Surgical Scissors"]

        elif "melanocytic nevi" in predict_result:
            recommendation_is = "Surgical removal for cosmetic consideration"
            link = "https://www.aad.org/public/diseases/a-z/moles-treatment"
            products = ["Surgical Scalpel", "Suture Kit"]

        elif "melanoma" in predict_result:
            recommendation_is = "Surgery"
            link = "https://www.cancer.org/cancer/melanoma-skin-cancer/treating/surgery.html"
            products = ["Surgical Instruments Set", "Electrosurgical Unit"]

        elif "pyogenic granulomas and hemorrhage; Vascular Tumor" in predict_result:
            recommendation_is = "Laser therapy"
            link = "https://www.aad.org/public/diseases/a-z/pyogenic-granuloma-treatment"
            products = ["CO2 Laser", "Pulsed Dye Laser"]

        elif "urticaria" in predict_result:
            recommendation_is = "Antihistamines"
            link = "https://www.mayoclinic.org/diseases-conditions/chronic-hives/diagnosis-treatment/drc-20352768"
            products = ["Cetirizine", "Loratadine"]

        elif "Lyme Disease and other Infestations and Bites" in predict_result:
            recommendation_is = "Antibiotics"
            link = "https://www.cdc.gov/lyme/treatment/index.html"
            products = ["Doxycycline", "Amoxicillin"]

        elif "Bullous Pemphigoid" in predict_result:
            recommendation_is = "Corticosteroids"
            link = "https://www.mayoclinic.org/diseases-conditions/bullous-pemphigoid/diagnosis-treatment/drc-20350719"
            products = ["Prednisone", "Clobetasol Cream"]

        elif "acne" in predict_result:
            recommendation_is = "Topical treatments"
            link = "https://www.aad.org/public/diseases/acne/causes/topical"
            products = ["Benzoyl Peroxide Gel", "Salicylic Acid Cleanser"]

        elif "rosacea" in predict_result:
            recommendation_is = "Topical treatments"
            link = "https://www.aad.org/public/diseases/rosacea/treatment"
            products = ["Metronidazole Cream", "Azelaic Acid Gel"]

        elif "vasculitis" in predict_result:
            recommendation_is = "Corticosteroids"
            link = "https://www.mayoclinic.org/diseases-conditions/vasculitis/diagnosis-treatment/drc-20363465"
            products = ["Prednisone", "Hydrocortisone Cream"]

        elif "Pigmentation Disorder" in predict_result:
            recommendation_is = "Topical treatments"
            link = "https://www.aad.org/public/diseases/a-z/hyperpigmentation-treatment"
            products = ["Hydroquinone Cream", "Retinoid Cream"]

        elif "herpes" in predict_result:
            recommendation_is = "Antiviral medication"
            link = "https://www.cdc.gov/std/herpes/treatment.htm"
            products = ["Acyclovir", "Valacyclovir"]

        elif "vascular tumor" in predict_result:
            recommendation_is = "Surgical removal or laser therapy"
            link = "https://www.cancer.gov/pediatric-adult-rare-tumor/rare-tumors/rare-vascular-tumors"
            products = ["Surgical Instruments Set", "CO2 Laser"]



        
    return render_template("prediction.html", prediction=predict_result, img_path=img_path, recommendation_result=recommendation_is,show_link=link,show_prod=products)

 
    
@app.route("/Graph")
def Graph():
	return render_template('Graph.html') 

@app.route("/chart")
def chart():
	return render_template('chart.html')