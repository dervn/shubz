import re
import datetime
import logging
from tornado.web import RequestHandler, HTTPError
from tornado.options import options
from tornado import escape
from jinja2 import TemplateNotFound

from bz.models.mixin import UserMixin
from bz.lib.filters import safe_markdown, xmldatetime, topiclink
from bz.lib.util import ObjectDict

class BaseHandler(RequestHandler, UserMixin):
    _first_run = True

    def initialize(self):
        if BaseHandler._first_run:
            logging.info('First Run')
            BaseHandler._first_run = False

    def finish(self, chunk=None):
        super(BaseHandler, self).finish(chunk)
        if self.get_status() == 500:
            try:
                self.db.commit()
            except:
                self.db.rollback()
            finally:
                self.db.commit()

    @property
    def db(self):
        return self.application.db

    @property
    def cache(self):
        return self.application.cache

    @property
    def env(self):
        return self.application.env

    def prepare(self):
        self._prepare_context()
        self._prepare_filters()

    def render_string(self, template_name, **kwargs):
        kwargs.update(self._filters)
        assert "context" not in kwargs, "context is a reserved keyword."
        kwargs["context"] = self._context
        return super(BaseHandler, self).render_string(template_name, **kwargs)

    def write(self, chunk):
        if isinstance(chunk, dict):
            chunk = escape.json_encode(chunk)
            callback = self.get_argument('callback', None)
            if callback:
                chunk = "%s(%s)" % (callback, escape.to_unicode(chunk))
                self.set_header("Content-Type",
                                "application/javascript; charset=UTF-8")
            else:
                self.set_header("Content-Type",
                                "application/json; charset=UTF-8")
        super(BaseHandler, self).write(chunk)

    def render(self, template, **args):
        try:
            template = self.env.get_template(template)
        except TemplateNotFound:
            raise HTTPError(404)

        #args['categories'] = Category.get_all_cat()

        self.env.globals['request']  = self.request
        self.env.globals['static_url'] = self.static_url
        self.env.globals['xsrf_form_html'] = self.xsrf_form_html
        self.write(template.render(args))

    def get_current_user(self):
        cookie = self.get_secure_cookie("user")
        if not cookie:
            return None
        try:
            id, token = cookie.split('/')
            id = int(id)
        except:
            self.clear_cookie("user")
            return None
        user = self.get_user_by_id(id)
        if not user:
            return None
        if token == user.token:
            return user
        self.clear_cookie("user")
        return None

    def is_owner_of(self, model):
        if not hasattr(model, 'user_id'):
            return False
        if not self.current_user:
            return False
        return model.user_id == self.current_user.id

    @property
    def next_url(self):
        next_url = self.get_argument("next", None)
        return next_url or '/'

    def _prepare_context(self):
        self._context = ObjectDict()
        self._context.now = datetime.datetime.utcnow()

        self._context.debug = options.debug
        self._context.message = []

    def _prepare_filters(self):
        self._filters = ObjectDict()
        self._filters.markdown = safe_markdown
        self._filters.xmldatetime = xmldatetime
        self._filters.topiclink = topiclink
        self._filters.get_user = self.get_user_by_id
        self._filters.is_mobile = self.is_mobile

    def create_message(self, header, body):
        msg = ObjectDict(header=header, body=body)
        self._context.message.append(msg)

    def is_mobile(self):
        _mobile = (r'ipod|iphone|android|blackberry|palm|nokia|symbian|'
                   r'samsung|psp|kindle|phone|mobile|ucweb|opera mini|fennec|'
                   r'webos')
        return True if re.search(_mobile, self.user_agent.lower()) else False

    def is_spider(self):
        _spider = r'bot|crawl|spider|slurp|search|lycos|robozilla|fetcher'
        return True if re.search(_spider, self.user_agent.lower()) else False

    def is_ajax(self):
        return "XMLHttpRequest" == self.request.headers.get("X-Requested-With")

    @property
    def user_agent(self):
        return self.request.headers.get("User-Agent", "bot")

class NoDestinationHandler(BaseHandler):
    def get(self):
        raise HTTPError(404)