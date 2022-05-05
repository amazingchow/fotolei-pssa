# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.abspath("./blueprint_factory"))
sys.path.append(os.path.abspath("./utils"))

import logging
import platform

from flask import Flask
from flask import has_request_context
from flask import request
from flask.logging import default_handler as flask_logging_default_handler
from flask_cors import CORS
from flask_session import Session

from blueprint_factory import association_blueprint
from blueprint_factory import case1_blueprint
from blueprint_factory import case2_blueprint
from blueprint_factory import case3_blueprint
from blueprint_factory import case4_blueprint
from blueprint_factory import case5_blueprint
from blueprint_factory import case6_blueprint
from blueprint_factory import case7_blueprint
from blueprint_factory import common_blueprint
from blueprint_factory import inventory_blueprint
from blueprint_factory import jit_inventory_blueprint
from blueprint_factory import option_blueprint
from blueprint_factory import product_blueprint
from blueprint_factory import selection_blueprint
from blueprint_factory import unit_price_blueprint
from blueprint_factory import user_blueprint


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
pssa_server.config["SEND_FILE_MAX_AGE_DEFAULT"] = 600
pssa_server.config["SECRET_KEY"] = "otwdd8but5"
pssa_server.config["PERMANENT_SESSION_LIFETIME"] = 86400
pssa_server.config["SESSION_PERMANENT"] = True
pssa_server.config["SESSION_USE_SIGNER"] = False
pssa_server.config["SESSION_KEY_PREFIX"] = "fotolei_pssa_server_session:"
pssa_server.config["SESSION_TYPE"] = "filesystem"
pssa_server.config["SESSION_FILE_MODE"] = 438  # 438的8进制表示就是666
pssa_server.config["SESSION_FILE_DIR"] = "{}/fotolei-pssa/session".format(os.path.expanduser("~"))
Session(pssa_server)
CORS(
    pssa_server,
    resources={r"/api/v1/*": {"origins": "*"}},
    expose_headers=["Set-Logged", "Set-User", "Set-Role"],
    supports_credentials=True
)
pssa_server.logger.setLevel(logging.INFO)
_RequestFormatter = RequestFormatter(
    "[%(asctime)s][%(levelname)s] %(remote_addr)s requested %(url)s - \n"
    "%(message)s"
)
flask_logging_default_handler.setFormatter(_RequestFormatter)
pssa_server.register_blueprint(association_blueprint)
pssa_server.register_blueprint(case1_blueprint)
pssa_server.register_blueprint(case2_blueprint)
pssa_server.register_blueprint(case3_blueprint)
pssa_server.register_blueprint(case4_blueprint)
pssa_server.register_blueprint(case5_blueprint)
pssa_server.register_blueprint(case6_blueprint)
pssa_server.register_blueprint(case7_blueprint)
pssa_server.register_blueprint(common_blueprint)
pssa_server.register_blueprint(inventory_blueprint)
pssa_server.register_blueprint(jit_inventory_blueprint)
pssa_server.register_blueprint(option_blueprint)
pssa_server.register_blueprint(product_blueprint)
pssa_server.register_blueprint(selection_blueprint)
pssa_server.register_blueprint(unit_price_blueprint)
pssa_server.register_blueprint(user_blueprint)


if __name__ == "__main__":
    # 初始化前的检查，检查是否已经生成系统依赖的自定义文件
    if platform.system() == "Linux":
        if not os.path.exists("{}/fotolei-pssa-keep/customize_report_forms_ui".format(os.path.expanduser("~"))):
            print("请先生成'customize_report_forms_ui'")
            sys.exit(-1)
    else:
        if not os.path.exists("{}/fotolei-pssa-keep/customize_report_forms_ui.db".format(os.path.expanduser("~"))):
            print("请先生成'customize_report_forms_ui'")
            sys.exit(-1)

    pssa_server.run(host="0.0.0.0", port=15555)
