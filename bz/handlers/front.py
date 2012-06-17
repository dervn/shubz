#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, time
from tornado.web import HTTPError
from tornado.options import options

from bz.lib.handler import BaseHandler

class IndexHandler(BaseHandler):
    def get(self):
        self.render("index.html")
