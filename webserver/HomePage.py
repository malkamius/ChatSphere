from flask import render_template, session
from flask_login import LoginManager, login_user, UserMixin, current_user
from flask.views import View
from shared.ansi_logger import getLogger

class HomePage(View):
    def __init__(self, model, template): #config, id_config, logger):
        self.config = model["config"]
        self.logger = getLogger(self.config, __name__)
        self.template = template
        
    def dispatch_request(self):
        # from .IdentityDbContext import UserManager

        # user_manager = UserManager()
        # user = None

        # if session["email"]:
            # user = user_manager.get_user_by_email(session["email"])
        return render_template(self.template)