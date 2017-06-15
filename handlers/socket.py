from storage import SOCKET
from tornado.websocket import WebSocketHandler
from methods import db
import time,calendar
import json

class PusheenSocket(WebSocketHandler):
    def check_origin(self,orig):
        return True
    def open(self):
        global SOCKET
        SOCKET.append(self)
        self.write_message(json.dumps({'state':'connection established.'}))
            #print(self.user)
    def on_message(self,msg):
        DANMAKU_SETTING=db.DanmakuSetting.find_one({"id":1})
        if msg=="ping":
            self.write_message(json.dumps({'state':'pong'}))
        else:   #recieved danmaku
            user_id=self.get_secure_cookie("user_id")
            #print(self.user_id.decode("utf-8"))
            #print("TT")
            if DANMAKU_SETTING["available"]==0:
                self.write_message(json.dumps({'state':'N'}))
            elif not user_id:
                #facebook not logged in
                self.write_message(json.dumps({'state':'L'}))
            else:
                user=db.Users.find_one({"user_id":user_id.decode("utf-8")})
            if user:
                msg_obj=json.loads(msg)
                if msg_obj["content"]==None:
                    self.write_message(json.dumps({'state':"Fuck you!!"})) #maybe the connection made by other application
                last_post_time=user['last_post_time']
                post_time=calendar.timegm(time.localtime())
                if msg_obj["content"]=="" or post_time-last_post_time < DANMAKU_SETTING["waiting_sec"]:
                    self.write_message(json.dumps({'state':str(DANMAKU_SETTING["waiting_sec"]-(post_time-last_post_time))}))
                else:
                    data={'state':'dan', 'user':user['first_name'], 'content':msg_obj["content"]}
                    msg_toq=json.dumps(data)
                    user['last_post_time']=post_time;
                    db.Users.replace_one({"user_id":user_id},user)
                    db.Messages.insert_one({'msg':msg_toq})
                    self.write_message(json.dumps({'state':str(DANMAKU_SETTING["waiting_sec"])}))
            else:
                #not registered
                self.write_message(json.dumps({'state':'R'}))
    def on_close(self):
        global SOCKET
        #print('WebSocket closed.')
        SOCKET.remove(self)
