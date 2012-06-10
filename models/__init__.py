#!/usr/bin/env python
# encoding: utf-8

"""
__init__.py
Created by dn on 2012/5/3.
Copyright (c) 2012 shubz. All rights reserved.
"""

import time
import hashlib
from random import choice
from datetime import datetime
from sqlalchemy import Column
from sqlalchemy import Integer, String, DateTime, Text
from tornado.options import options
from data import db

def get_current_impact():
    return int(time.time())

def create_token(length=16):
    chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    salt = ''.join([choice(chars) for i in range(length)])
    return salt


class User(db.Model):
    name = Column(String(128), unique=True, index=True)
    email = Column(String(128), unique=True, nullable=False, index=True)
    password = Column(String(128), nullable=False)
