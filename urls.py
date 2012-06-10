#!/usr/bin/env python
# encoding: utf-8

from handlers import front,account
handlers = []
handlers.extend(front.handlers)
handlers.extend(account.handlers)

from dashboard import handlers as dashboard
handlers.extend(dashboard.handlers)

ui_modules = {}
ui_modules.update(front.ui_modules)
