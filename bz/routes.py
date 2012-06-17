#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import tornado.web

from bz.handlers import front, account

handlers = [
      (r"/", front.IndexHandler),
]