from flask import jsonify, request
from flask.views import MethodView
from shared.ansi_logger import getLogger
class HandlerStopProcessing(MethodView):
    def __init__(self, model):
        super()

        self.config = model["config"]
        self.logger = getLogger(self.config, __name__)
    
    def get(self):
        return jsonify({})
    
    def post(self):
        sessionid = request.args.get("sessionid")
        response = {
                "sessionid": sessionid,
                "message": "Stopping generation"
            }
        
        self.logger.debug("Submitted request")

        return jsonify(response)
