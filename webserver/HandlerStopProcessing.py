from flask import jsonify, request
from flask.views import MethodView
from shared.ansi_logger import getLogger
from .DataDbContext import DataDbContext
from flask_login import UserMixin, current_user

class HandlerStopProcessing(MethodView):
    def __init__(self, model):
        super()

        self.config = model["config"]
        self.logger = getLogger(self.config, __name__)
    
    def get(self):
        return jsonify({})
    
    def post(self):
        sessionid = request.args.get("sessionid")
        if current_user.is_authenticated:
            user_id = current_user.id
        else:
            user_id = "0000"
        if sessionid != None:
            db_context = DataDbContext(self.config)
            if db_context.cancel_request(user_id, sessionid):
                response = {
                        "sessionid": sessionid,
                        "message": "Stopping generation"
                    }
            else:
                response = {
                        "sessionid": sessionid,
                        "message": "No requests to cancel"
                    }
            self.logger.debug("Cancel Request")
        else:
            response = {"sessionid": sessionid, "message": "Invalid Session ID"}
        
        return jsonify(response)
