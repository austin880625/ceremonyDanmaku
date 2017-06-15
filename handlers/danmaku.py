import tornado.web
import time,calendar
import json
from storage import fetch_key,appid
from methods import db
from urllib import request,parse

def update_state(new_danmaku_state, new_program):
    data={'state':'upd', 'dan':new_danmaku_state, 'program':new_program}
    if data['dan']==None:
        data.pop('dan',None)
    if data['program']==None:
        data.pop('program',None)
    msg=json.dumps(data)
    db.Messages.insert_one({'msg':msg})

class DanMaKuPage(tornado.web.RequestHandler):
    def get(self):
        DANMAKU_SETTING=db.DanmakuSetting.find_one({"id":1})
        if DANMAKU_SETTING==None:
            DANMAKU_SETTING={"id":1,"program":"準備中...","available":1,"waiting_sec":30}
            db.DanmakuSetting.insert_one(DANMAKU_SETTING)
        self.render("danmaku2.html",program=DANMAKU_SETTING["program"],appid=appid)

class SendDanMaKu(tornado.web.RequestHandler):
    def get(self):
        DANMAKU_SETTING=db.DanmakuSetting.find_one({"id":1})
        WAITING_SEC=DANMAKU_SETTING["waiting_sec"]
        user_id=self.get_secure_cookie("user_id")
        if DANMAKU_SETTING["available"]==0:
            self.write("N")
        elif not user_id:
            self.write("L")
        else:
            user=db.Users.find_one({"user_id":user_id.decode("utf-8")})
            if user==None:
                self.write("R")
            else:
                #print(user)
                last_post_time=user['last_post_time']
                post_time=calendar.timegm(time.localtime())
                #print(str(post_time-last_post_time).encode("utf-8"))
                self.write(str(WAITING_SEC-(post_time-last_post_time)).encode("utf-8"))
    def post(self):
        DANMAKU_SETTING=db.DanmakuSetting.find_one({"id":1})
        WAITING_SEC=DANMAKU_SETTING["waiting_sec"]
        content=self.get_argument('content')
        user_id=self.get_secure_cookie("user_id")
        #print(user_id)
        if DANMAKU_SETTING["available"]==0:
            self.write("N")
        elif not user_id:
            self.write("L")
        else:
            user_id=user_id.decode("utf-8")
            user=db.Users.find_one({"user_id":user_id})
            if user==None:
                self.write("R")
            else:
                #print(user)
                last_post_time=user['last_post_time']
                post_time=calendar.timegm(time.localtime())
                #print(str(post_time-last_post_time).encode("utf-8"))
                if post_time-last_post_time < WAITING_SEC:
                    self.write(str(WAITING_SEC-(post_time-last_post_time)).encode("utf-8"))
                else:
                    data={'state':'dan', 'user':user['first_name'], 'content':content}
                    msg=json.dumps(data)
                    user['last_post_time']=post_time;
                    db.Users.replace_one({"user_id":user_id},user)
                    db.Messages.insert_one({'msg':msg})
                    self.write(str(WAITING_SEC))
#        fb_raw_response=request.urlopen('https://graph.facebook.com/me',data={'access_token':'user_fb_token'})
#        fb_response=json.loads(fb_raw_response.read())


class Register(tornado.web.RequestHandler):
    def post(self):
        user_fb_token=self.get_argument('user_fb_token')
        user_id=self.get_argument('user_id')
        user=db.Users.find_one({"user_id":user_id})
        if user==None:
            fb_raw_response=request.urlopen('https://graph.facebook.com/'+user_id+'?fields=first_name,last_name&locale=zh_TW&access_token='+user_fb_token)#,parse.urlencode({'access_token':user_fb_token}).encode('utf-8')
            fb_response=json.loads(fb_raw_response.read().decode("utf-8"))
            first_name=fb_response['first_name']
            if len(first_name)==1:
                first_name=fb_response["last_name"]+first_name
            db.Users.insert_one({'user_id':user_id, 'first_name':first_name, 'last_post_time':0})
        self.set_secure_cookie("user_id",user_id)
        #else:
        #    print('registered')
        #print(user_id)
        #print(user_fb_token)

        self.write("success")

class ChangeLimit(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin","*")
        self.set_header("Access-Control-Allow-Headers","x-requested-with")
        self.set_header("Access-Control-Allow-Methods",'POST')
    def post(self):
        DANMAKU_SETTING=db.DanmakuSetting.find_one({"id":1})
        key=self.get_argument("fetch_key")
        if key==None:
            self.write("YEE")
        else:
            if not key==fetch_key:
                self.write("YEE")
            else:
                new_danmaku_state=self.get_argument("state",default=None)
                new_limit=self.get_argument("second",default=None)
                new_program=self.get_argument("program",default=None)
                if (not new_limit==None) and (not new_limit==""):
                    DANMAKU_SETTING["waiting_sec"]=int(new_limit)
                if not new_danmaku_state==None:
                    if new_danmaku_state=="0":
                        DANMAKU_SETTING["available"]=0
                    else:
                        DANMAKU_SETTING["available"]=1
                if not new_program==None:
                    DANMAKU_SETTING["program"]=new_program
                db.DanmakuSetting.replace_one({"id":1},DANMAKU_SETTING)
                update_state(new_danmaku_state,new_program)
                self.write("S")
