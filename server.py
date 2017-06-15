#!/usr/bin/env Python
#coding=utf-8

import tornado.ioloop
import tornado.options
import tornado.httpserver

from tornado import gen
import datetime
from methods import db
from storage import SOCKET

from application import application

from tornado.options import define, options

define("port", default=8000, help="run on the given port", type=int)


@gen.coroutine
def check_new_message():
    global SOCKET
    cursor=db.Messages.find({},cursor_type=db.CursorType.TAILABLE_AWAIT)
    while cursor.alive:
        try:
            doc=cursor.next()
            #print('sending to recipient...')
            for socket in SOCKET:
                yield socket.write_message(doc["msg"])
            #print('done.')
        except StopIteration:
            yield gen.Task(tornado.ioloop.IOLoop.current().add_timeout,datetime.timedelta(milliseconds=100))

if __name__ == "__main__":
    tornado.options.parse_command_line()
    Pusheen=tornado.httpserver.HTTPServer(application)
    Pusheen.listen(options.port, address='0.0.0.0')

    check_new_message()
    tornado.ioloop.IOLoop.instance().start()
