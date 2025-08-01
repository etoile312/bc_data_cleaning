# file: xfyun_tts.py

import base64
import hashlib
import hmac
import json
import time
import websocket
import threading
import ssl
import os
from urllib.parse import quote_plus  # ⬅️ 需要添加

# 讯飞开放平台提供的信息
APPID = "f2382e9b"
APIKey = "536786a723b23189c5a417b0c8ca2e3f"
APISecret = "N2M4ZGVmNGNhODllMzI0ZmQ1MGRiMWFl"

# WebSocket 地址（固定）
HOST = "tts-api.xfyun.cn"
URL = "wss://tts-api.xfyun.cn/v2/tts"

class WsParam:
    def __init__(self, appid, api_key, api_secret):
        self.APPID = appid
        self.APIKey = api_key
        self.APISecret = api_secret

    def create_url(self):
        # 生成鉴权参数
        now = int(time.time())
        date = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(now))
        signature_origin = f"host: {HOST}\ndate: {date}\nGET /v2/tts HTTP/1.1"
        signature_sha = hmac.new(self.APISecret.encode('utf-8'),
                                 signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(signature_sha).decode('utf-8')

        authorization = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature}"'
        #auth_base64 = base64.b64encode(authorization.encode('utf-8')).decode('utf-8')
        auth_base64 = base64.b64encode(authorization.encode('utf-8')).decode('utf-8')

        params = f"?authorization={quote_plus(auth_base64)}&date={quote_plus(date)}&host={quote_plus(HOST)}"
        #params = f"?authorization={auth_base64}&date={date}&host={HOST}"
        return URL + params

def save_and_exit(mp3_bytes, filename):
    with open(filename, "wb") as f:
        f.write(mp3_bytes)
    print("✔ 语音文件保存成功：", filename)

def generate_tts(text, filename="output.mp3", voice="秀英", speed=50):
    ws_param = WsParam(APPID, APIKey, APISecret)
    url = ws_param.create_url()
    mp3_bytes = bytearray()

    def on_message(ws, message):
        data = json.loads(message)
        if data["code"] != 0:
            print("❌ 错误:", data["code"], data["message"])
            ws.close()
            return
        audio = base64.b64decode(data["data"]["audio"]) 
        mp3_bytes.extend(audio)
        if data["data"]["status"] == 2:  # 最后一帧
            save_and_exit(mp3_bytes, filename)
            ws.close()

    def on_error(ws, error):
        print("❌ WebSocket 错误:", error)

    def on_close(ws, close_status_code, close_msg):
        print(f"🔌 WebSocket 关闭: code={close_status_code}, msg={close_msg}")


    def on_open(ws):
        frame = {
            "common": {
                "app_id": APPID
            },
            "business": {
                "aue": "lame",          # mp3
                "vcn": voice,           # 声音角色，如 xiaoju
                "speed": speed,         # 语速 0-100
                "volume": 50,
                "pitch": 50,
                "bgs": 0
            },
            "data": {
                "status": 2,
                "text": base64.b64encode(text.encode('utf-8')).decode('utf-8')
            }
        }
        ws.send(json.dumps(frame))

    websocket.enableTrace(False)
    ws = websocket.WebSocketApp(url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close,
                                on_open=on_open)
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

# 示例调用：
if __name__ == "__main__":
    text = "你好，我下次治疗什么时候"
    generate_tts(text, filename="audio/xiaoju_output.mp3", voice="秀英")
