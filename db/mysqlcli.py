# -*- coding: utf-8 -*-
import logging
logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s][%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)
import mysql.connector
import os

from mysql.connector import errorcode
from singleton import Singleton


@Singleton
class MySQLConnector():
    def __init__(self):
        self.host = os.environ.get("MYSQL_HOST")
        if self.host == None or len(self.host) == 0:
            raise Exception("MYSQL_HOST must be set!!!")
        self.port = os.environ.get("MYSQL_PORT")
        if self.port == None or len(self.port) == 0:
            raise Exception("MYSQL_PORT must be set!!!")
        self.username = os.environ.get("MYSQL_USERNAME")
        if self.username == None or len(self.username) == 0:
            raise Exception("MYSQL_USERNAME must be set!!!")
        self.password = os.environ.get("MYSQL_PASSWORD")
        if self.password == None or len(self.password) == 0:
            raise Exception("MYSQL_PASSWORD must be set!!!")

    def init_conn(self, db:str):
        try:
            self.cnx = mysql.connector.connect(
                host=self.host, port=self.port, 
                user=self.username, passwd=self.password, 
                database=db, allow_local_infile=True
            )
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                raise Exception("Invalid MYSQL_USERNAME or MYSQL_PASSWORD")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                raise Exception("Database {} does not exist".format(db))
            else:
                raise Exception("Unknown err: {}".format(err))
        
        if not self.cnx.is_connected():
            raise Exception("MySQL Server can not be connected ({}:{}@{}:{})".format(
                self.username, self.password, self.host, self.port
            ))
        else:
            logger.debug("Connect to MySQL Server ({}:{})".format(
                self.host, self.port
            ))

        self.cur = self.cnx.cursor()

    def release_conn(self):
        self.cur.close()
        self.cnx.disconnect()
        logger.debug("Disconnect from MySQL Server ({}:{})".format(
            self.host, self.port
        ))

    def insert_sql(self, sql:str, records:list):
        for record in records:
            if type(record) != dict:
                raise Exception("Input record must be dict type")
            try:
                self.cur.execute(sql, record)
                self.cnx.commit()
            except mysql.connector.Error as err:
                self.cnx.rollback()
                logger.error("INSERT err: {}".format(err))

    def load_data_infile(self, sql:str):
        try:
            self.cur.execute(sql)
            self.cnx.commit()
        except mysql.connector.Error as err:
            self.cnx.rollback()
            logger.error("LOAD DATA INFILE err: {}".format(err))

    def query_sql(self, sql:str):
        self.cur.execute(sql)
        return self.cur.fetchall()
    
    def update_sql(self, sql:str):
        pass

    def delete_sql(self, sql:str):
        pass
