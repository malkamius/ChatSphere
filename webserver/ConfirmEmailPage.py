from flask import render_template, redirect, url_for, abort, request, flash
from flask.views import View
import uuid
from flask_mail import Mail, Message
from shared.ansi_logger import getLogger


class ConfirmEmailPage(View):
    methods = ["GET"]
    def __init__(self, model, template):
        self.config = model["config"]
        self.logger = getLogger(self.config, __name__)
        self.user_manager = model["user_manager"]
        self.template = template
        
    def dispatch_request(self):
        
        email = request.args.get("email")
        token = request.args.get("token")
        
        user = self.user_manager.get_user(email_address=email)
        if user.confirm_uuid == token and not user.email_confirmed:
            user.email_confirmed = True
            self.user_manager.update_user(user)
            error = None
        else:
            error = "Account not found, already confirmed, or invalid token."
            #flash("Account not found, already confirmed, or invalid token.")

        return render_template(self.template, error=error)