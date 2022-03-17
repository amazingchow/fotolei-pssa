# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.abspath("./blueprint_factory"))
from blueprint_factory import blueprint
sys.path.append(os.path.abspath("./utils"))
from utils import db_connector
from flask import Flask
from flask_cors import CORS

pssa_server = Flask(__name__)
pssa_server.config.from_object(__name__)
CORS(pssa_server, resources={r"/api/*": {"origins": "*"}})
pssa_server.register_blueprint(blueprint)
