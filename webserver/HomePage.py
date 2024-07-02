from flask import render_template, session, request
from flask_login import current_user
from flask.views import View
from shared.ansi_logger import getLogger
from .DataDbContext import DataDbContext
import json

class HomePage(View):
    def __init__(self, model, template): #config, id_config, logger):
        self.config = model["config"]
        self.logger = getLogger(self.config, __name__)
        self.template = template
        
    def dispatch_request(self):
        if current_user.is_authenticated:
            user_id = current_user.id
        else:
            user_id = "0000"
        
        sessionid = request.args.get("sessionid", default="0000")
        requestid = request.args.get("requestid")
        messagelength = request.args.get("messagelength")

        if sessionid != None:
            db_context = DataDbContext(self.config)
            messages = db_context.retrieve_session_requests(user_id, sessionid, count = 100)
        else:
            messages = []

        messages_json = json.dumps(messages)
        
        return render_template(self.template, messages_json=messages_json)