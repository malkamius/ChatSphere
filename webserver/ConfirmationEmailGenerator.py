from flask import url_for, redirect, render_template
from flask_mail import Mail, Message
from shared.ansi_logger import getLogger

def generate_confirmation_email(mail, email, confirmation_token):
    confirm_url = url_for('/Account/ConfirmEmail', token=confirmation_token, email=email, _external=True)
    if mail:
        html = render_template('confirm_email_email_template.html', confirm_url=confirm_url)
        subject = "Please confirm your email"
        msg = Message(subject, recipients=[email], html=html)
        msg.body = f"To confirm you have access to this email, you must navigate with a web browser to the link \n{confirm_url}"
        mail.send(msg)
        return redirect(url_for('/EmailConfirmationSent'))
    else:
        return redirect(confirm_url)