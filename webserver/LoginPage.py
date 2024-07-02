from flask import render_template, request, redirect, url_for
from flask_login import login_user
from flask.views import View
from .IdentityDbContext import UserManager
from .User import User
from shared.ansi_logger import getLogger

class LoginPage(View):
    methods = ["GET", "POST"]
    
    def __init__(self, model, template):
        self.config = model["config"]
        self.logger = getLogger(self.config, __name__)
        self.user_manager: UserManager = model["user_manager"]
        self.template = template

        if not isinstance(self.user_manager, UserManager):
            raise TypeError("user_manager must be an instance of UserManager")
        
    def execute_and_render_invalid_username_or_password(self, user: User):
        if user != None:
            self.user_manager.fail_login_attempt(user)

        return render_template(self.template, error_text='Invalid username or password.')
    
    def dispatch_request(self):
        if request.method == 'POST':
            # Handle POST request
            email = request.form.get('Input.Email', None)
            password = request.form.get('Input.Password', None)
            
            user = self.user_manager.get_user_by_email(email)

            if user:
                if user.locked_out:
                    return render_template(self.template, error_text='User locked out. Please wait a while and try again.')
                elif not user.email_confirmed:
                    return render_template(self.template, error_text='You have not confirmed your email address yet.')
                elif user.check_password(password):
                    login_user(user, remember=True)
                    return redirect(url_for('/Index'))
                else:
                    return self.execute_and_render_invalid_username_or_password(user)
            else:
                return self.execute_and_render_invalid_username_or_password(None)
        return render_template(self.template)