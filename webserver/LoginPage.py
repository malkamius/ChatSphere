from flask import render_template, request, session, redirect, url_for
from flask_login import login_user, current_user
from flask.views import View

class LoginPage(View):
    methods = ["GET", "POST"]
    
    def __init__(self, model, template):
        self.config = model["config"]
        self.logger = model["logger"]
        self.user_manager = model["user_manager"]
        self.template = template
        
    def dispatch_request(self):
        if request.method == 'POST':
            # Handle POST request
            email = request.form.get('Input.Email', None)
            password = request.form.get('Input.Password', None)
            
            user = self.user_manager.get_user_by_email(email);
            if user:
                if user.locked_out:
                    return render_template(self.template, error_text='User locked out. Please wait a while and try again.')
                elif not user.email_confirmed:
                    return render_template(self.template, error_text='You have not confirmed your email address yet.')
                elif user.check_password(password):
                    login_user(user, remember=True)
                    return redirect(url_for('/Index'))
                else:
                    return render_template(self.template, error_text='Invalid username or password.')
            else:
                return render_template(self.template, error_text='Invalid username or password.')
        return render_template(self.template)