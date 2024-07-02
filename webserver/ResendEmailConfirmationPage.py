from flask import render_template, redirect, url_for, abort, flash
from flask.views import View
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
import uuid
from flask_mail import Mail, Message
from .ConfirmationEmailGenerator import generate_confirmation_email
from .IdentityDbContext import UserManager
from shared.ansi_logger import getLogger

class EmailForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send')

    def __init__(self, user_manager: UserManager, logger):
        self.user_manager = user_manager
        self.logger = logger
        super().__init__()

    def validate_email(self, email):
        user_exists = self.user_manager.get_user_by_email(email.data)
        
        if (not user_exists) or user_exists.email_confirmed:
            raise ValidationError('An account with that email does not exist or it has already been confirmed.')

class ResendEmailConfirmationPage(View):
    methods = ["GET", "POST"]
    def __init__(self, model, template):
        self.config = model["config"]
        self.logger = getLogger(self.config, __name__)
        self.user_manager = model["user_manager"]
        self.mail = model["mail"]
        self.template = template
        
    def dispatch_request(self):
        form = EmailForm(self.user_manager, self.logger)
        if form.validate_on_submit():
            try:
                confirmation_token = str(uuid.uuid4())
                user = self.user_manager.get_user_by_email(form.email.data)
                user.confirm_uuid = confirmation_token
                self.user_manager.update_user(user)

                return generate_confirmation_email(self.mail, form.email.data, confirmation_token)
            except ValidationError as e:
                flash(str(e))
            except Exception as e:
                abort(400)

            
        
        return render_template(self.template, form=form)