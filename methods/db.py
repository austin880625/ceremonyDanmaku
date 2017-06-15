from  pymongo import MongoClient, CursorType
Client=MongoClient('localhost',27017)
Database=Client.main_database
Users=Database.users
DanmakuSetting=Database.danmakuSetting
#capped
Messages=Database.messages
