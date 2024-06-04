from flask_login import UserMixin
import uuid

class User(UserMixin):
    id = None
    username = None
    email = None
    password = None
    active = True
    locked_out = False
    security_stamp = None
    
    def __init__(self, bcrypt, id, username, email, password, security_stamp, active, locked_out, email_confirmed):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.security_stamp = security_stamp
        self.active = True
        self.locked_out = locked_out
        self.email_confirmed = email_confirmed
        self.bcrypt = bcrypt
        
    def set_password(self, password):
        self.security_stamp =  str(uuid.uuid4())
        self.password = self.bcrypt.generate_password_hash(password + self.security_stamp).decode('utf-8')
        
    def check_password(self, password):
        return self.bcrypt.check_password_hash(self.password, password + self.security_stamp)

    def __repr__(self):
        return self.email