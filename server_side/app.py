from flask import Flask
from server_side.routes import routes
from flask_cors import CORS
import logging

class Server:
    def __init__(self, community, port=8080):
        self.community = community
        self.port = port
        self.app = Flask(__name__)
        CORS(self.app)
        routes(self.app, community)

    def start(self):
        """Run the Flask server on the main thread"""
        logging.info(f"Starting server on port {self.port}")
        self.app.run(host='0.0.0.0', port=self.port)