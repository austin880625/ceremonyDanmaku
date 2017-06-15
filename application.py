#!/usr/bin/env Python
# coding=utf-8

from urls import urls

import tornado.web
import os

settings=dict(
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "statics"),
    static_url_prefix= "/resources/",
)

application=tornado.web.Application(urls, **settings,cookie_secret="6aa1c13a594ecd09cc7c3fee83b93bc3",debug=True)
