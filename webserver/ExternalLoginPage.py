from flask import render_template
from flask.views import View
from shared.ansi_logger import getLogger

class ExternalLoginPage(View):
    def __init__(self, model, template):
        self.config = model["config"]
        self.logger = getLogger(self.config, __name__)
        self.template = template
        
    def dispatch_request(self):
        return render_template(self.template)