#!/usr/bin/env python
# encoding: utf-8

"""
main.py
Created by dn on 2012/5/3.
Copyright (c) 2012 shubz. All rights reserved.
"""

import os
import logging
import tornado
from tornado import web
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.options import define, options
from tornado.httpserver import HTTPServer
from jinja2 import Environment, FileSystemLoader

from lib.util import parse_config_file

FILTERS = {}

class Application(web.Application):
    def __init__ (self):

        from data import db, cache  # init db
        from urls import handlers, ui_modules

        settings = dict(
            debug = options.debug,
            static_path = os.path.join(os.path.dirname(__file__), "static"),
            static_url_prefix = options.static_url_prefix,
            cookie_secret = options.cookie_secret,
            xsrf_cookies = True,
            login_url = options.login_url,

            ui_modules=ui_modules,
        )

        super(Application, self).__init__(handlers, **settings)

        Application.db = db.session
        Application.cache = cache

        template_path = os.path.join(os.path.dirname(__file__), "templates"),
        self.env = Environment(
                loader=FileSystemLoader(template_path),
                extensions = [
                                'jinja2.ext.i18n',
                             ],
                )
        self.env.filters = FILTERS
        self.env.install_null_translations(newstyle=True)
        self.env.globals['cfg'] = settings

        logging.info("load finished!")

def main():

    parse_config_file(os.path.join(os.path.dirname(__file__), 'config.cfg'))
    tornado.options.parse_command_line()

    http_server = HTTPServer(Application(), xheaders=True)
    http_server.bind(options.port)
    http_server.start()

    IOLoop.instance().start()

if __name__ == "__main__":
    main()