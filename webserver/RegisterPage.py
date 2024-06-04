from flask import render_template
from flask.views import View

class RegisterPage(View):
    methods = ["GET", "POST"]
    def __init__(self, model, template):
        self.config = model["config"]
        self.logger = model["logger"]
        self.template = template
        
    def dispatch_request(self):
        return render_template(self.template)