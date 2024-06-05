from flask import render_template, redirect, url_for, session
from flask_login import LoginManager, login_user, UserMixin, current_user, logout_user, login_required
from flask.views import View

class LogoutPage(View):
    #decorators = [login_required]
    def __init__(self, model, template):
        self.config = model["config"]
        self.logger = model["logger"]
        self.template = template
        
    def dispatch_request(self):
        logout_user()
        return redirect(url_for('/Index'))