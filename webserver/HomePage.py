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
            sessionid = request.args.get("sessionid")
            requestid = request.args.get("requestid")
            messagelength = request.args.get("messagelength")
            
            db_context = DataDbContext(self.config)

            sessions = db_context.retrieve_sessions(user_id)

            if sessionid != None:
                
                messages = db_context.retrieve_session_requests(user_id, sessionid, count = 100)
            else:
                messages = []

            messages_json = json.dumps(messages)
            sessions_json = json.dumps(sessions)
            return render_template(self.template, 
                                   messages_json=messages_json, 
                                   sessions_json = sessions_json,
                                   sessionid = sessionid)
        else:
            return render_template(self.template)    
