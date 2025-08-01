from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Body
from pydantic import BaseModel
from typing import List, Optional, Union
import os
import json
import httpx
import threading
import time
try:
    import simpleaudio as sa
except ImportError:
    sa = None

# 全局播放控制（可扩展为多session控制）
playback_flags = {}

app = FastAPI()

# 占位符：阿里云TTS配置
#ALIYUN_ACCESS_KEY_ID = "<your-access-key-id>"
#ALIYUN_ACCESS_KEY_SECRET = "<your-access-key-secret>"
ALIYUN_ACCESS_KEY_ID = "LTAI5tHBH5UcRyiq2fJsqMvM"
ALIYUN_ACCESS_KEY_SECRET = "Ub0T41PM9Y1v1dL2zg7EARU3RNaWgW"
ALIYUN_TTS_ENDPOINT = "https://nls-gateway.cn-beijing.aliyuncs.com/stream/v1/tts"

# 角色与voice参数映射
ROLE_VOICE = {
    "patient": "xiaoyun",  # 患者用女声 
    "doctor": "xiaogang"   # 医生用男声
}

# 音频输出目录
AUDIO_DIR = "audio_output"
os.makedirs(AUDIO_DIR, exist_ok=True)

class DialogueItem(BaseModel):
    role: str  # 'patient' or 'doctor'
    text: str

class DialogueUpload(BaseModel):
    dialogue: Union[str, List[DialogueItem]]

# 工具：解析上传的对话文本

def parse_dialogue(dialogue: Union[str, List[dict]]) -> List[DialogueItem]:
    result = []
    if isinstance(dialogue, str):
        # 假设格式为“患者：... 医生：...”
        lines = [l.strip() for l in dialogue.split('\n') if l.strip()]
        for line in lines:
            if line.startswith("患者：") or line.startswith("患者:"):
                result.append(DialogueItem(role="patient", text=line.split("：",1)[-1] if "：" in line else line.split(":",1)[-1]))
            elif line.startswith("医生：") or line.startswith("医生:"):
                result.append(DialogueItem(role="doctor", text=line.split("：",1)[-1] if "：" in line else line.split(":",1)[-1]))
    elif isinstance(dialogue, list):
        for item in dialogue:
            if isinstance(item, dict) and "role" in item and "text" in item:
                result.append(DialogueItem(role=item["role"], text=item["text"]))
    return result

@app.post("/upload_dialogue")
def upload_dialogue(dialogue: Union[str, List[DialogueItem]] = Body(...)):
    """
    上传对话文本，支持：
    1. 纯文本（带“患者：”“医生：”前缀）
    2. 结构化JSON（[{"role":..., "text":...}, ...]）
    """
    # 解析对话
    try:
        # 尝试解析为JSON
        if isinstance(dialogue, str):
            try:
                parsed = json.loads(dialogue)
                items = parse_dialogue(parsed)
            except Exception:
                items = parse_dialogue(dialogue)
        else:
            # 如果是Pydantic模型列表，转为dict再传递
            items = parse_dialogue([item.dict() for item in dialogue])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"对话解析失败: {e}")
    if not items:
        raise HTTPException(status_code=400, detail="未解析到有效对话内容")
    # 保存为临时文件
    session_id = str(len(os.listdir(AUDIO_DIR)))
    session_dir = os.path.join(AUDIO_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)
    with open(os.path.join(session_dir, "dialogue.json"), "w", encoding="utf-8") as f:
        json.dump([item.dict() for item in items], f, ensure_ascii=False, indent=2)
    return {"session_id": session_id, "count": len(items), "msg": "对话上传并解析成功，后续可调用TTS合成接口。"}

# 预留：TTS合成与循环播放接口，后续实现

def aliyun_tts(text: str, voice: str, output_path: str) -> bool:
    """
    调用阿里云TTS接口，将text合成为output_path音频文件。
    返回True成功，False失败。
    """
    headers = {
        "X-NLS-Token": "<your-access-token>",  # 推荐用token，或用AK签名（此处为占位）
        "Content-Type": "application/json"
    }
    payload = {
       # "appkey": "<your-app-key>",  # 占位
        "appkey": "LEfxy82Yv2i6WHQT", 
        "text": text,
       # "token": "<your-access-token>",
        "token": "18e6fd7f34e7412a9c9e7342a08aa4c0",
        "format": "wav",
        "sample_rate": 16000,
        "voice": voice,
        "volume": 50,
        "speech_rate": 0,
        "pitch_rate": 0
    }
    try:
        with httpx.stream("POST", ALIYUN_TTS_ENDPOINT, headers=headers, json=payload, timeout=30.0) as response:
            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    for chunk in response.iter_bytes():
                        f.write(chunk)
                return True
            else:
                print(f"TTS请求失败: {response.status_code}, {response.text}")
                return False
    except Exception as e:
        print(f"TTS请求异常: {e}")
        return False

@app.post("/synthesize_audio")
def synthesize_audio(session_id: str):
    """
    合成指定session_id的对话音频，按角色分配voice。
    """
    session_dir = os.path.join(AUDIO_DIR, session_id)
    dialogue_path = os.path.join(session_dir, "dialogue.json")
    if not os.path.exists(dialogue_path):
        raise HTTPException(status_code=404, detail="未找到对应对话数据")
    with open(dialogue_path, "r", encoding="utf-8") as f:
        items = json.load(f)
    audio_files = []
    for idx, item in enumerate(items):
        role = item.get("role", "patient")
        text = item.get("text", "")
        voice = ROLE_VOICE.get(role, "xiaoyun")
        audio_path = os.path.join(session_dir, f"audio_{idx+1}_{role}.wav")
        ok = aliyun_tts(text, voice, audio_path)
        if not ok:
            raise HTTPException(status_code=500, detail=f"TTS合成失败: {role}-{idx+1}")
        audio_files.append(audio_path)
    return {"audio_files": audio_files, "msg": "音频合成成功"}

def play_audio_files(audio_files, loop=True, stop_flag=None):
    """
    循环播放音频文件列表，音频间隔1秒，整轮间隔3秒。
    stop_flag: threading.Event()，用于外部停止播放。
    """
    if sa is None:
        print("simpleaudio 未安装，无法播放音频。请 pip install simpleaudio")
        return
    while loop and (stop_flag is None or not stop_flag.is_set()):
        for audio_path in audio_files:
            if stop_flag is not None and stop_flag.is_set():
                break
            if not os.path.exists(audio_path):
                print(f"音频文件不存在: {audio_path}")
                continue
            try:
                wave_obj = sa.WaveObject.from_wave_file(audio_path)
                play_obj = wave_obj.play()
                play_obj.wait_done()
            except Exception as e:
                print(f"播放失败: {audio_path}, {e}")
            time.sleep(1)
        time.sleep(3)

@app.post("/loop_playback")
def loop_playback(session_id: str):
    """
    远程调用，循环播放指定session_id下的所有音频。
    """
    session_dir = os.path.join(AUDIO_DIR, session_id)
    audio_files = [os.path.join(session_dir, f) for f in os.listdir(session_dir) if f.endswith('.wav')]
    audio_files.sort()  # 按文件名顺序
    if not audio_files:
        raise HTTPException(status_code=404, detail="未找到音频文件，请先合成音频")
    # 启动后台线程循环播放
    stop_flag = threading.Event()
    playback_flags[session_id] = stop_flag
    t = threading.Thread(target=play_audio_files, args=(audio_files, True, stop_flag), daemon=True)
    t.start()
    return {"msg": f"已开始循环播放 session {session_id} 的音频，可通过 /stop_playback 停止。"}

@app.post("/stop_playback")
def stop_playback(session_id: str):
    """
    停止指定session_id的循环播放。
    """
    flag = playback_flags.get(session_id)
    if flag:
        flag.set()
        return {"msg": f"已停止 session {session_id} 的循环播放。"}
    else:
        return {"msg": f"未找到 session {session_id} 的播放任务。"}
