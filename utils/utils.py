# -*- coding: utf-8 -*-
import hashlib
import logging
import time
from functools import wraps

logging.basicConfig(level=logging.INFO, format="[%(asctime)s][%(levelname)s] %(message)s")
logger = logging.getLogger("FlaskApp")


def cost_count(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        t = func(*args, **kwargs)
        logger.info("%s tooks time: %f secs", func.__name__, time.time()-start)
        return t
    return wrapper


def generate_file_digest(f: str):
    sha256_hash = hashlib.sha256()
    with open(f, "rb") as fin:
        for byte_block in iter(lambda: fin.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def generate_digest(s: str):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()
