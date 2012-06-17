#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
main.py
Created by dn on 2012/6/17.
Copyright (c) 2012 shubz. All rights reserved.
"""
import os
PROJDIR = os.path.abspath(os.path.dirname(__file__))
ROOTDIR = os.path.split(PROJDIR)[0]

import logging
import tornado
from tornado import web
from tornado.options import options
from bz.lib.util import reset_option

reset_option('debug', True, type=bool)
reset_option('port', 8000, type=int)
reset_option('autoescape', None)

# site config
reset_option('sitename', 'Bz', type=str)

reset_option('static_path', os.path.join(PROJDIR, '_static'))
reset_option('static_url_prefix', '/static/', type=str)
reset_option('template_path', os.path.join(PROJDIR, "_templates"))

reset_option('locale_path', os.path.join(PROJDIR, '_locale'))
reset_option('login_url', '/account/signin', type=str)

# mysql & memcache
reset_option('mysql', '', type=str)
reset_option('slaves', '', type=str)
reset_option('memcache', '', type=str)

# third party support config
reset_option('gravatar_base_url', "http://www.gravatar.com/avatar/")
reset_option('gravatar_extra', '')

class Application(tornado.web.Application):
    def __init__ (self):

        settings = dict(
            debug=options.debug,
            autoescape=options.autoescape,
            cookie_secret=options.cookie_secret,
            xsrf_cookies=True,
            login_url=options.login_url,

            template_path=options.template_path,
            static_path=options.static_path,
            static_url_prefix=options.static_url_prefix,

        )
        from bz.routes import handlers
        super(Application, self).__init__(handlers, **settings)

        # init db & cache
        from bz.data import db, cache
        Application.db = db.session
        Application.cache = cache

        # load template
        from jinja2 import Environment, FileSystemLoader
        self.env = Environment(loader=FileSystemLoader(options.template_path), extensions = [
            'jinja2.ext.i18n',
            'bz.lib.jinja2htmlcompress.HTMLCompress'])
        #Custom Filters
        self.env.filters = {
        }
        self.env.install_null_translations(newstyle=True)
        self.env.globals['cfg'] = settings

        import bz
        logging.info("load finished, version %s" % bz.__version__ )

def run_server():

    from bz.lib.util import parse_config_file
    parse_config_file(os.path.join(ROOTDIR, 'setting.py'))
    tornado.options.parse_command_line()

    from tornado.httpserver import HTTPServer
    http_server = HTTPServer(Application(), xheaders=True)
    http_server.bind(options.port)
    http_server.start()

    tornado.ioloop.IOLoop.instance().start()
