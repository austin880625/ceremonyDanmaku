#!/usr/bin/env Python
# coding=utf-8

from handlers.danmaku import SendDanMaKu,Register,DanMaKuPage,ChangeLimit
from handlers.socket import PusheenSocket

urls = [
    (r'/', DanMaKuPage),
    (r'/danmaku', DanMaKuPage),
    (r'/senddanmaku', SendDanMaKu),
    (r'/Pusheen', PusheenSocket),
    (r'/register', Register),
    (r'/changelimit', ChangeLimit),
]
