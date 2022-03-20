# -*- coding: utf-8 -*-
import os

import logging
import logging.handlers
_rotate_file_handler = logging.handlers.WatchedFileHandler(
    filename="{}/fotolei-pssa/logs/fotolei-pssa-db.log".format(os.path.expanduser("~")),
    mode="a"
)
_rotate_file_handler_formatter = logging.Formatter(
    "[%(asctime)-15s][%(levelname)-5s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
_rotate_file_handler.setFormatter(_rotate_file_handler_formatter)
_db_logger = logging.getLogger("FotoleiPssA_DB")
_db_logger.setLevel(logging.INFO)
_db_logger.addHandler(_rotate_file_handler)
# TODO: is log-file-append atomic in unix?
# See: https://stackoverflow.com/questions/1154446/is-file-append-atomic-in-unix
import time

import mysql.connector as mc
import mysql.connector.errorcode as mc_errorcode
import mysql.connector.pooling as mc_pooling

from functools import wraps


def db_r_w_cost_count(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        t = func(*args, **kwargs)
        _db_logger.info("%s took time: %f secs", func.__name__, time.time() - start)
        return t
    return wrapper


class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator, not a metaclass, to the class
    that should be a singleton.

    The decorated class can define one `__init__` function that takes
    only the `self` argument. Also, the decorated class cannot be
    inherited from. Other than that, there are no restrictions that
    apply to the decorated class.

    To get the singleton instance, use the `instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.
    """

    def __init__(self, decorated):
        self._decorated = decorated

    def instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.
        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError("The singleton instance must be accessed through `instance()`.")

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)


@Singleton
class MySQLConnector():
    def __init__(self):
        self._host = os.environ.get("MYSQL_HOST", "127.0.0.1")
        self._port = os.environ.get("MYSQL_PORT", "13306")
        self._usr = os.environ.get("MYSQL_USERNAME", "root")
        self._pwd = os.environ.get("MYSQL_PASSWORD", "Pwd123Pwd")

    def init_conn_pool(self, db: str):
        try:
            db_config = {
                "host": self._host,
                "port": self._port,
                "user": self._usr,
                "password": self._pwd,
                "database": db,
                "allow_local_infile": True
            }
            self._cnx_pool = mc_pooling.MySQLConnectionPool(
                pool_size=8, pool_name="fotolei-pssa-db-conn-pool",
                pool_reset_session=True, **db_config
            )
        except mc.Error as err:
            if err.errno == mc_errorcode.ER_ACCESS_DENIED_ERROR:
                raise Exception("Invalid username or password.")
            elif err.errno == mc_errorcode.ER_BAD_DB_ERROR:
                raise Exception("Database {} does not exist.".format(db))
            else:
                raise Exception("Unknown err: {}.".format(err))

    def __exit__(self):
        # TODO: how to release the pooling resources?
        _db_logger.info("Disconnect from MySQL Server ({}:{})".format(
            self._host, self._port
        ))

    @db_r_w_cost_count
    def insert(self, stmt: str, record: tuple):
        cnx = self._cnx_pool.get_connection()
        cur = cnx.cursor()
        try:
            cur.execute(stmt, record)
            cnx.commit()
        except mc.Error as err:
            cnx.rollback()
            _db_logger.error("INSERT err: {}".format(err))
        finally:
            cur.close()
            cnx.close()

    @db_r_w_cost_count
    def batch_insert(self, stmt: str, records: list):
        cnx = self._cnx_pool.get_connection()
        cur = cnx.cursor()
        try:
            cur.executemany(stmt, records)
            cnx.commit()
        except mc.Error as err:
            cnx.rollback()
            _db_logger.error("BATCH-INSERT err: {}".format(err))
        finally:
            cur.close()
            cnx.close()

    @db_r_w_cost_count
    def load_data_infile(self, stmt: str):
        cnx = self._cnx_pool.get_connection()
        cur = cnx.cursor()
        try:
            cur.execute(stmt)
            cnx.commit()
        except mc.Error as err:
            cnx.rollback()
            _db_logger.error("LOAD DATA INFILE err: {}".format(err))
        finally:
            cur.close()
            cnx.close()

    @db_r_w_cost_count
    def query(self, stmt: str):
        cnx = self._cnx_pool.get_connection()
        cur = cnx.cursor()
        result = object()
        try:
            cur.execute(stmt)
            result = cur.fetchall()
        except mc.Error as err:
            _db_logger.error("QUERY err: {}".format(err))
        finally:
            cur.close()
            cnx.close()
        return result

    @db_r_w_cost_count
    def update(self, stmt: str):
        cnx = self._cnx_pool.get_connection()
        cur = cnx.cursor()
        try:
            cur.execute(stmt)
            cnx.commit()
        except mc.Error as err:
            cnx.rollback()
            _db_logger.error("UPDATE err: {}".format(err))
        finally:
            cur.close()
            cnx.close()

    @db_r_w_cost_count
    def batch_update(self, stmt: str, records: list):
        cnx = self._cnx_pool.get_connection()
        cur = cnx.cursor()
        try:
            cur.executemany(stmt, records)
            cnx.commit()
        except mc.Error as err:
            cnx.rollback()
            _db_logger.error("UPDATE err: {}".format(err))
        finally:
            cur.close()
            cnx.close()

    @db_r_w_cost_count
    def delete(self, stmt: str):
        cnx = self._cnx_pool.get_connection()
        cur = cnx.cursor()
        try:
            cur.execute(stmt)
            cnx.commit()
        except mc.Error as err:
            cnx.rollback()
            _db_logger.error("DELETE err: {}".format(err))
        finally:
            cur.close()
            cnx.close()

    @db_r_w_cost_count
    def create_table(self, stmt: str):
        cnx = self._cnx_pool.get_connection()
        cur = cnx.cursor()
        try:
            cur.execute(stmt)
            cnx.commit()
        except mc.Error as err:
            cnx.rollback()
            _db_logger.error("CREATE TABLE err: {}".format(err))
        finally:
            cur.close()
            cnx.close()

    @db_r_w_cost_count
    def drop_table(self, stmt: str):
        cnx = self._cnx_pool.get_connection()
        cur = cnx.cursor()
        try:
            cur.execute(stmt)
            cnx.commit()
        except mc.Error as err:
            cnx.rollback()
            _db_logger.error("DELETE TABLE err: {}".format(err))
        finally:
            cur.close()
            cnx.close()
