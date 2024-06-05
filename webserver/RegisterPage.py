from flask import render_template, redirect, url_for, abort
from flask.views import View
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
import uuid
from flask_mail import Mail, Message
from .ConfirmationEmailGenerator import generate_confirmation_email
from .IdentityDbContext import UserManager

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirmpassword = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register')

    def __init__(self, user_manager: UserManager, logger):
        self.user_manager = user_manager
        self.logger = logger
        super().__init__()

    def validate_email(self, email):
        user_exists = self.user_manager.get_user_by_email(email.data)
        
        if user_exists:
            raise ValidationError('Email is already in use. Please choose a different one.')

class RegisterPage(View):
    methods = ["GET", "POST"]
    def __init__(self, model, template):
        self.config = model["config"]
        self.logger = model["logger"]
        self.user_manager = model["user_manager"]
        self.mail = model["mail"]
        self.template = template
        
    def dispatch_request(self):
        form = RegisterForm(self.user_manager, self.logger)
        if form.validate_on_submit():
            #try:
            confirmation_token = str(uuid.uuid4())
            self.user_manager.create_user(form.email.data, form.password.data, confirmation_token)
            
            generate_confirmation_email(self.mail, form.email.data, confirmation_token)
            return redirect(url_for('/EmailConfirmationSent'))
            #except Exception as e:
            #    abort(400)

            
        
        return render_template(self.template, form=form)