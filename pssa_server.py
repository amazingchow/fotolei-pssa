# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.abspath("./blueprint_factory"))
sys.path.append(os.path.abspath("./utils"))

import logging

from flask import Flask
from flask import has_request_context
from flask import request
from flask.logging import default_handler as flask_logging_default_handler
from flask_cors import CORS

from blueprint_factory import blueprint


class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
        else:
            record.url = None
            record.remote_addr = None
        return super().format(record)


pssa_server = Flask(__name__)
pssa_server.config.from_object(__name__)
pssa_server.logger.setLevel(logging.INFO)
_RequestFormatter = RequestFormatter(
    "[%(asctime)s][%(levelname)s] %(remote_addr)s requested %(url)s - \n"
    "%(message)s"
)
flask_logging_default_handler.setFormatter(_RequestFormatter)
CORS(pssa_server, resources={r"/api/v1/*": {"origins": "*"}})
pssa_server.register_blueprint(blueprint)


if __name__ == "__main__":
    pssa_server.run(host="0.0.0.0", port=15555)
