# -*- coding: utf-8 -*-
from .db import MySQLConnector

db_connector = MySQLConnector.instance()
db_connector.init_conn_pool("fotolei_pssa")

__all__ = [
    db_connector
]
