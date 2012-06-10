#!/usr/bin/env python
# encoding: utf-8

"""
front.py
Created by dn on 2012/5/3.
Copyright (c) 2012 shubz. All rights reserved.
"""

import os, time
from tornado.web import HTTPError
from tornado.options import options

from lib.handler import BaseHandler

class IndexHandler(BaseHandler):
    def get(self):
        self.render("index.html")

handlers = [
    (r"/", IndexHandler),
]

ui_modules = {

}