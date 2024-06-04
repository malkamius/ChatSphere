from flask import Flask, session
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, UserMixin, current_user

from .HomePage import HomePage
from .RegisterPage import RegisterPage
from .LoginPage import LoginPage
from .LogoutPage import LogoutPage
from .ForgotPasswordPage import ForgotPasswordPage
from .ResendEmailConfirmationPage import ResendEmailConfirmationPage
from .ExternalLoginPage import ExternalLoginPage


from shared.config import DevelopmentConfig
from shared.ansi_logger import getLogger
from shared.identity_db_config import IdentityDevelopmentConfig

from .IdentityDbContext import UserManager

id_config = IdentityDevelopmentConfig()

config = DevelopmentConfig()
logger = getLogger(config, __name__)

app = Flask(__name__)

app.secret_key = config.SESSION_SECRET_KEY

login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = '/Account/Login'
bcrypt = Bcrypt(app)

user_manager = UserManager(logger, bcrypt)
# admin = user_manager.get_user_by_email("cking999@gmail.com")
# admin.set_password("test123")
# user_manager.update_user(admin)

@login_manager.user_loader
def load_user(user_id):
    result = user_manager.get_user_by_id(user_id)
    return result

home_page = HomePage.as_view("Home", {'config': config, 'id_config': id_config, 'logger': logger}, "index.html") #(config, id_config, logger)
register_page = RegisterPage.as_view("Register", {'config': config, 'id_config': id_config, 'logger': logger}, "register.html") #(config, id_config, logger)
login_page = LoginPage.as_view("Login", {'config': config, 'id_config': id_config, 'logger': logger, 'user_manager': user_manager}, "login.html") #(config, id_config, logger, user_manager)
logout_page = LogoutPage.as_view("Logout", {'config': config, 'id_config': id_config, 'logger': logger}, "logout.html") #(config, id_config, logger)
forgot_password_page = ForgotPasswordPage.as_view("ForgotPassword", {'config': config, 'id_config': id_config, 'logger': logger}, "forgot_password.html") #(config, id_config, logger)
resend_email_confirmation_page = ResendEmailConfirmationPage.as_view("ResendConfirmationEmail", {'config': config, 'id_config': id_config, 'logger': logger}, "resend_confirmation_email.html") #(config, id_config, logger)
external_login_page = ExternalLoginPage.as_view("ExternalLogin", {'config': config, 'id_config': id_config, 'logger': logger}, "external_login.html") #(config, id_config, logger)

# Create a dictionary mapping paths to handler methods
routes = {
    '/': {'handler': home_page, 'methods': ['GET']},
    '/Index': {'handler': home_page, 'methods': ['GET']},
    '/Account/Register': {'handler': register_page, 'methods': ['GET', 'POST']},
    '/Account/Login': {'handler': login_page, 'methods': ['GET', 'POST']},
    '/Account/Logout': {'handler': logout_page, 'methods': ['GET']},
    '/Account/ForgotPassword': {'handler': forgot_password_page, 'methods': ['GET','POST']},
    '/Account/ResendEmailConfirmation': {'handler': resend_email_confirmation_page, 'methods': ['GET','POST']},
    '/Account/ExternalLogin': {'handler': external_login_page, 'methods': ['GET','POST']},
}

# Register the routes with Flask
for path, route_info in routes.items():
    app.add_url_rule(path, view_func=route_info['handler'], endpoint=path, methods=route_info['methods'])

if __name__ == "__main__":
    app.run(debug=True)