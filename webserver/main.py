import os
import json


from flask import Flask, session, send_from_directory
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
from .ConfirmEmailPage import ConfirmEmailPage
from .ConfirmationEmailSentPage import ConfirmationEmailSentPage

from .HandlerCheckMessages import HandlerCheckMessages
from .HandlerSendMessage import HandlerSendMessage
from .HandlerStopProcessing import HandlerStopProcessing

from shared.config import DevelopmentConfig
from shared.ansi_logger import getLogger
from shared.identity_db_config import IdentityDevelopmentConfig

from .IdentityDbContext import UserManager
from flask_mail import Mail, Message
from flask_wtf.csrf import CSRFProtect

def run():
    id_config = IdentityDevelopmentConfig()

    config = DevelopmentConfig()
    logger = getLogger(config, __name__)

    app = Flask(__name__)

    app.secret_key = config.SESSION_SECRET_KEY
    app.config['SECURITY_PASSWORD_SALT'] = config.SESSION_SECRET_KEY
    csrf = CSRFProtect(app)
    login_manager = LoginManager(app)
    login_manager.init_app(app)
    login_manager.login_view = '/Account/Login'
    bcrypt = Bcrypt(app)

    user_manager = UserManager(config, bcrypt)


    # Get the current directory of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    def load_secrets(path):
        if os.path.exists(path):
            with open(path, 'r') as file:
                return json.load(file)    
        return None

    # Construct the path to the email_secrets.json file
    secrets_file_path = os.path.join(script_dir, '..', 'live-secrets', 'secrets.json')
    secrets = load_secrets(secrets_file_path)

    secrets_file_path = os.path.join(script_dir, '..', 'secrets', 'secrets.json')
    if not secrets:
        secrets = load_secrets(secrets_file_path)

    app.config['MAIL_SERVER'] = secrets["mail-server"]
    app.config['MAIL_PORT'] = secrets["mail-port"]
    app.config['MAIL_USE_TLS'] = secrets["mail-TLS"]
    app.config['MAIL_USERNAME'] = secrets["mail-email"]
    app.config['MAIL_PASSWORD'] = secrets["mail-password"]
    app.config['MAIL_DEFAULT_SENDER'] = secrets["mail-email"]

    mail = None

    if app.config['MAIL_SERVER'] != "" and app.config['MAIL_USERNAME'] != "":
        mail = Mail(app)

    # admin = user_manager.get_user_by_email("cking999@gmail.com")
    # admin.set_password("test123")
    # user_manager.update_user(admin)

    @login_manager.user_loader
    def load_user(user_id):
        result = user_manager.get_user_by_id(user_id)
        return result

    home_page = HomePage.as_view("Home", {'config': config, 'id_config': id_config, 'logger': logger}, "index.html")
    register_page = RegisterPage.as_view("Register", {'config': config, 'id_config': id_config, 'logger': logger, 'user_manager': user_manager, "mail": mail}, "register.html")
    login_page = LoginPage.as_view("Login", {'config': config, 'id_config': id_config, 'logger': logger, 'user_manager': user_manager}, "login.html")
    logout_page = LogoutPage.as_view("Logout", {'config': config, 'id_config': id_config, 'logger': logger}, "logout.html")
    forgot_password_page = ForgotPasswordPage.as_view("ForgotPassword", {'config': config, 'id_config': id_config, 'logger': logger, 'user_manager': user_manager}, "forgot_password.html")
    resend_email_confirmation_page = ResendEmailConfirmationPage.as_view("ResendConfirmationEmail", {'config': config, 'id_config': id_config, 'logger': logger, 'user_manager': user_manager, "mail": mail}, "resend_confirmation_email.html") #(config, id_config, logger)
    external_login_page = ExternalLoginPage.as_view("ExternalLogin", {'config': config, 'id_config': id_config, 'logger': logger, 'user_manager': user_manager}, "external_login.html")
    confirm_email = ConfirmEmailPage.as_view("ConfirmEmail", {'config': config, 'id_config': id_config, 'logger': logger, 'user_manager': user_manager}, "confirm_email.html")
    confirmation_email_sent = ConfirmationEmailSentPage.as_view("ConfirmationEmailSent", {'config': config, 'logger': logger}, "confirmation_email_sent.html")

    handler_check_messages = HandlerCheckMessages.as_view("check_messages", {'config': config})
    handler_send_message = HandlerSendMessage.as_view("send_message", {'config': config})
    handler_stop_processing = HandlerStopProcessing.as_view("stop_processing", {'config': config})

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
        '/Account/ConfirmEmail': {'handler': confirm_email, 'methods': ['GET']},
        '/EmailConfirmationSent': {'handler': confirmation_email_sent, 'methods': ['GET']},
        '/send_message': {'handler': handler_send_message, 'methods': ['POST']},
        '/check_messages': {'handler': handler_check_messages, 'methods': ['GET']},
        '/stop_processing': {'handler': handler_stop_processing, 'methods': ['POST']},
    }

    # Register the routes with Flask
    for path, route_info in routes.items():
        app.add_url_rule(path, view_func=route_info['handler'], endpoint=path, methods=route_info['methods'])

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(app.static_folder, 'favicon.ico')
    
    app.run(host=config.WEB_SERVER, port=config.WEB_PORT, debug=config.DEBUG)
    
if __name__ == "__main__":
    run()