from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Email, ValidationError,EqualTo
from flask_login import current_user

from .models import User

class RegisterForm(FlaskForm):
    username = StringField('User Name', validators=[Length(min=2, max=30), DataRequired()])
    email = StringField('E-mail', validators=[Email(), DataRequired()])
    password1 = PasswordField('Password', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField('Confirm Password', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField('Create Account')

    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError('Username already exists! Please try a different username.')

    def validate_email(self, email_to_check):
        email = User.query.filter_by(email=email_to_check.data).first()
        if email:
            raise ValidationError('Email Address already exists! Please try a different email address.')

class LoginForm(FlaskForm):
    username = StringField('User Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign in')

class UpdateProfileForm(FlaskForm):
    username = StringField(label='User Name', validators=[Length(min=2, max=30), DataRequired()])
    email = StringField(label='E-mail', validators=[Email(), DataRequired()])
    submit = SubmitField(label='Update Profile')

    def validate_username(self, username_to_check):
        if username_to_check.data != current_user.username:
            user = User.query.filter_by(username=username_to_check.data).first()
            if user:
                raise ValidationError('Username already exists! Please try a different username')

    def validate_email(self, email_to_check):
        if email_to_check.data != current_user.email:
            email = User.query.filter_by(email=email_to_check.data).first()
            if email:
                raise ValidationError('Email Address already exists! Please try a different email address')
