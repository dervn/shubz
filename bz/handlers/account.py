#!/usr/bin/env python
# encoding: utf-8

"""
account.py
Created by dn on 2012/5/3.
Copyright (c) 2012 shubz. All rights reserved.
"""

import os, time
import tornado.web
from tornado.web import HTTPError
from tornado.options import options

from lib.handler import BaseHandler
from lib import validators
from lib.util import ObjectDict

class SigninHandler(BaseHandler):
    def head(self):
        pass

    def get(self):
        if self.current_user:
            return self.redirect(self.next_url)
        self.render('signin.html')

    def post(self):
        account = self.get_argument('account', None)
        password = self.get_argument('password', None)
        if not (account and password):
            self.create_message('Form Error', 'Please fill the required field')
            self.render('signin.html')
            return
        if '@' in account:
            user = User.query.filter_by(email=account).first()
        else:
            user = User.query.filter_by(username=account).first()
        if user and user.check_password(password):
            self.set_secure_cookie('user', '%s/%s' % (user.id, user.token))
            self.redirect(self.next_url)
            self.create_log(user.id)
            return
        self.create_message('Form Error', "Invalid account or password")
        self.render('signin.html')

    def create_log(self, user_id):
        ip = self.request.remote_ip
        log = UserLog(user_id=user_id, ip=ip, message='Signin')
        self.db.add(log)
        self.db.commit()

class SignupHandler(BaseHandler):
    def head(self):
        pass

    def get(self):
        if self.current_user:
            return self.redirect(self.next_url)
        self.render('signup.html')

    @tornado.web.asynchronous
    def post(self):
        email = self.get_argument('email', None)
        password1 = self.get_argument('password1', None)
        password2 = self.get_argument('password2', None)
        if not (email and password1 and password2):
            self.create_message('Form Error', 'Please fill the required field')
            return self.render('signup.html', email=email)

        validate = True
        if not validators.email(email):
            validate = False
            self.create_message('Form Error', 'Not a valid email address')

        if password1 != password2:
            validate = False
            self.create_message('Form Error', "Password doesn't match")

        if not validate:
            #recaptcha = self.recaptcha_render()
            #self.render('signup.html', email=email, recaptcha=recaptcha)
            return self.render('signup.html', email=email)

        user = User.query.filter_by(email=email).first()
        if user:
            self.create_message('Form Error',
                                "This email is already registered")
            return self.render('signup.html', email=email)

        self.recaptcha_validate(self._on_validate)

    def _on_validate(self, response):
        email = self.get_argument('email', None)
        password = self.get_argument('password1', None)
        if not response:
            self.create_message('Form Error', 'Captcha not valid')
            return self.render('signup.html', email=email)
        user = self.create_user(email)
        user.password = user.create_password(password)
        self.db.add(user)
        self.db.commit()
        self.cache.delete('status')
        self.set_secure_cookie('user', '%s/%s' % (user.id, user.token))
        return self.redirect(self.next_url)

class SignoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie('user')
        self.redirect(self.next_url)

handlers = [
    (r"/signin", SigninHandler),
    (r"/signup", SignupHandler),
]
