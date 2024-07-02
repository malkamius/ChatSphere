from flask import jsonify, request
from flask.views import MethodView
from shared.ansi_logger import getLogger
from flask_login import UserMixin, current_user
from .DataDbContext import DataDbContext

class HandlerCheckMessages(MethodView):
    def __init__(self, model):
        super()

        self.config = model["config"]
        self.logger = getLogger(self.config, __name__)

    def get(self):
        if current_user.is_authenticated:
            user_id = current_user.id
        else:
            user_id = "0000"
        
        sessionid = request.args.get("sessionid")
        requestid = request.args.get("requestid")
        messagelength = request.args.get("messagelength")

        if sessionid != None and requestid != None and messagelength != None:
            db_context = DataDbContext(self.config)
            reponse_text = db_context.get_request_response(user_id, sessionid, requestid, messagelength)
            response = {
                    "sessionid": sessionid,
                    "requestid": requestid,
                    "message": reponse_text
                }
        
        self.logger.debug("Checked messages")
        return jsonify(response)
    
    def post(self):
        return jsonify({"error": "Post not supported."})
