from flask import jsonify, request
from flask.views import MethodView
from shared.ansi_logger import getLogger
class HandlerCheckMessages(MethodView):
    def __init__(self, model):
        super()

        self.config = model["config"]
        self.logger = getLogger(self.config, __name__)

    def get(self):
        sessionid = request.args.get("sessionid")
        messagelength = request.args.get("messagelength")

        response = {
                "sessionid": sessionid,
                "message": "This is a simulated response."
            }
        
        self.logger.debug("Checked messages")
        return jsonify(response)
    
    def post(self):
        return jsonify({"error": "Post not supported."})
