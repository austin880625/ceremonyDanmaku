# Ceremony Danmaku
基本的典禮播放影片用的彈幕系統，主要使用tornado框架
##Screenshot
![Alt text](/screenshot.png "screenshot")

## Feature
### 彈幕伺服器
* 首頁即為彈幕發送頁面
* 以Facebook帳號登入（需創建Facebook app）
* 從頁面上的文字框發送後，彈幕就會顯示在頁面並在台上的影片播放器上飄過

### 影片播放器
* 一個有基本影片播放、切換功能的頁面（支援mp4）
* 連線至彈幕伺服器後，即啟用彈幕功能，台下觀眾可以連上彈幕網站發送彈幕
* 可以控制發送彈幕的冷卻時間、更新典禮進度、開啟關閉彈幕功能
* 可用於典禮的影片播放與台下觀眾互動

## Requirements
* python 3
* tornado web server
* mongo DB server

## Usage
1. 安裝python所需套件：
```
python3 -m pip install -r requirements.txt
```
3. 修改Facebook app ID以及cookie_secret：
在storage.py中：
```python3
#change this value to ensure security
cookie_secret="6aa1c13a594ecd09cc7c3fee83b93bc3"
#this must match with the one in video.html
fetch_key="73e5b233e2c2e8d19527a20f3259ebcc"
#Your Facebook app id
appid="XXXXXXXXXXXXXXXXXX"
```
PS：Facebook App的設定記得新增web平台，並將site url更改為網站的URL

3. 啟動伺服器：
```
sudo service mongod start
python3 server.py
```
4. 建立capped collection（作為訊息隊列）：
先進入mogodb shell
```
mongo
```
依序執行以下指令：
```
use main_database
db.createCollection("messages",{ capped: true, size: 204800 })
exit
```
5. 影片播放器設定：
* 滑鼠移到頁面左下角按「連線」後輸入彈幕伺服器位置，觀眾連上彈幕網站的首頁即可開始使用
* 在「連線」旁的文字框輸入影片檔案名稱（在同一資料夾，不須加副檔名）後按「載入」後即可以「播放」、「暫停」按鈕控制影片進度
* 右邊兩個文字框一個用來更新典禮進度，一個可用來更新彈幕的冷卻時間
