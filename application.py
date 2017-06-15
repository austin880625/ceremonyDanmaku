#!/usr/bin/env Python
# coding=utf-8

from urls import urls
from storage import cookie_secret
import tornado.web
import os

settings=dict(
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "statics"),
    static_url_prefix= "/resources/",
)

application=tornado.web.Application(urls, **settings,cookie_secret=cookie_secret,debug=True)
