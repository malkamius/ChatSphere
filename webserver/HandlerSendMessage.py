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
        else:
            user_id = "0000"
        
        if data and 'message' in data:
            
            message = data['message']
            
            try:
                db_context = DataDbContext(self.config)
            
                requestid = db_context.create_new_request(user_id, "0000", message)

                response = {
                    "sessionid": 
                    "0000", 
                    "requestid": requestid, 
                    "message": f"You: {message}"}
            except Exception as e:
                response = {"sessionid": "0000", "message": f"Error creating request: {str(e)}"} 
        else:
            response = {"sessionid": "0000", "message": f"Error creating request: Invalid input"} 
        return jsonify(response)
