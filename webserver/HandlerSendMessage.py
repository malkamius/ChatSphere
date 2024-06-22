from flask import jsonify, request
from flask.views import MethodView
from shared.ansi_logger import getLogger
class HandlerSendMessage(MethodView):
    def __init__(self, model):
        super()
        self.config = model["config"]
        self.logger = getLogger(self.config, __name__)

    def get(self):
        return jsonify({})

    def post(self):
        data = request.get_json()  # Parse JSON data
        if data and 'message' in data:
            message = data['message']
            response = {"sessionid": "0000", "message": f"Received: {message}"}
            return jsonify(response)
        return jsonify({"error": "Invalid input"}), 400
