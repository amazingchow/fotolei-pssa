# -*- coding: utf-8 -*-
import hashlib


def generate_file_digest(f: str):
    sha256_hash = hashlib.sha256()
    with open(f, "rb") as fin:
        for byte_block in iter(lambda: fin.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def generate_digest(s: str):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()
