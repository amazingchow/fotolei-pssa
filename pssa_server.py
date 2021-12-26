# -*- coding: utf-8 -*-
import atexit
import os
import sys
sys.path.append(os.path.abspath("./blueprint_module"))
from blueprint_module import blueprint
sys.path.append(os.path.abspath("./utils"))
from utils import db_connector
from flask import Flask
from flask_cors import CORS

pssa_server = Flask(__name__)
pssa_server.config.from_object(__name__)
CORS(pssa_server, resources={r"/api/*": {"origins": "*"}})
pssa_server.register_blueprint(blueprint)


def all_done():
    db_connector.release_conn()

atexit.register(all_done)
