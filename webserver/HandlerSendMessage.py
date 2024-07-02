from flask import jsonify, request
from flask.views import MethodView
from shared.ansi_logger import getLogger
from .DataDbContext import DataDbContext
from flask_login import UserMixin, current_user

class HandlerSendMessage(MethodView):
    def __init__(self, model):
        super()
        self.config = model["config"]
        self.logger = getLogger(self.config, __name__)

    def get(self):
        return jsonify({})

    def post(self):
        data = request.get_json()  # Parse JSON data
        if current_user.is_authenticated:
            user_id = current_user.id
            if data and 'message' in data:
                db_context = DataDbContext(self.config)
                message = data['message']
                if 'sessionid' in data and data['sessionid'] and data['sessionid'] != "None":
                    sessionid = data['sessionid']
                    self.logger.info(f"EXISTING SESSION: {sessionid}")
                else:
                    self.logger.info("CREATING SESSION")
                    sessionid = db_context.create_new_session(user_id)

                sessionname = db_context.retrieve_session_name(user_id, sessionid)

                if sessionname is None:
                    response = {"sessionid": "", "message": f"Error creating request: You do not have access to that session"} 
                else:
                    try:                    
                        requestid = db_context.create_new_request(user_id, sessionid, message)

                        response = {
                            "sessionid": sessionid,
                            "sessionname": sessionname,
                            "requestid": requestid, 
                            "message": f"You: {message}"}
                    except Exception as e:
                        response = {"sessionid": "", "message": f"Error creating request: {str(e)}"} 
            else:
                response = {"sessionid": "", "message": f"Error creating request: Invalid input"} 
        else:
            response = {"sessionid": "", "message": f"Must be authenticated to send messages"} 
        
        return jsonify(response)
