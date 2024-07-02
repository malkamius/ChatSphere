from flask import render_template, redirect, url_for, abort
from flask.views import View
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from shared.ansi_logger import getLogger

class ConfirmationEmailSentPage(View):
    methods = ["GET"]
    def __init__(self, model, template):
        self.config = model["config"]
        self.logger = getLogger(self.config, __name__)
        self.template = template
        
    def dispatch_request(self):
        return render_template(self.template)