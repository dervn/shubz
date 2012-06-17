#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import tornado.web

from handlers import front, account

routes = [
      (r"/", front.IndexHandler),
]