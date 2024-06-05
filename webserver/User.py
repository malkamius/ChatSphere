from flask_login import UserMixin
import uuid
from flask_bcrypt import Bcrypt

class User(UserMixin):
    id = None
    username = None
    email = None
    password = None
    active = True
    locked_out = False
    security_stamp = None
    confirm_uuid = None
    email_confirmed = False

    def __init__(self, bcrypt: Bcrypt, id: str, username: str, email: str, password: str, security_stamp: str, active: bool, locked_out: bool, email_confirmed, confirm_uuid):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.security_stamp = security_stamp
        self.active = True
        self.locked_out = locked_out
        self.email_confirmed = email_confirmed
        self.confirm_uuid = confirm_uuid
        self.bcrypt = bcrypt

    def set_password(self, password: str):
        self.security_stamp =  str(uuid.uuid4())
        self.password = self.bcrypt.generate_password_hash(password + self.security_stamp).decode('utf-8')
        
    def check_password(self, password: str):
        return self.bcrypt.check_password_hash(self.password, password + self.security_stamp)

    def __repr__(self):
        return self.email