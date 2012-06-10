#!/usr/bin/env python
# encoding: utf-8

"""
mixin.py
Created by dn on 2012/5/3.
Copyright (c) 2012 shubz. All rights reserved.
"""

from lib.decorators import cache
from models import create_token
from models import User

def get_cache_list(handler, model, id_list, key_prefix, time=600):
    if hasattr(handler, 'cache'):
        cache = handler.cache
    else:
        cache = handler.handler.cache
    if not id_list:
        return {}
    id_list = set(id_list)
    data = cache.get_multi(id_list, key_prefix=key_prefix)
    missing = id_list - set(data)
    if missing:
        dct = {}
        for item in model.query.filter_by(id__in=missing).all():
            dct[item.id] = item

        cache.set_multi(dct, time=time, key_prefix=key_prefix)
        data.update(dct)

    return data


class UserMixin(object):
    @cache('user', 600)
    def get_user_by_id(self, id):
        return User.query.filter_by(id=id).first()

    @cache("user", 600)
    def get_user_by_email(self, email):
        return User.query.filter_by(email=email).first()

    def get_users(self, id_list):
        return get_cache_list(self, User, id_list, 'user:')
