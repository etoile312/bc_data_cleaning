# FastAPI TTS Dialogue Project

## 项目简介
本项目基于 FastAPI，支持上传患者-医生对话文本，自动调用阿里云 TTS（文字转语音）接口，将文本合成语音（患者和医生为不同声音），并支持远程循环播放合成音频。

## 主要功能
- 支持上传两种格式的对话：
  1. 标有“患者/医生”前缀的一整段文本（如“患者：... 医生：...”）。
  2. 结构化 JSON 格式的问答对（如 [{"role": "patient", "text": "..."}, {"role": "doctor", "text": "..."}]）。
- 自动分割文本，按角色调用阿里云 TTS 合成音频。
- 患者和医生分别使用不同的声音参数。
- 服务器端自动循环播放合成音频，音频之间间隔1秒，每轮播放结束间隔3秒。
- 提供远程接口触发播放。

## 依赖
- fastapi
- uvicorn
- pydantic
- httpx

## 快速开始
1. 克隆本项目并进入目录：
   ```bash
   git clone <your-repo-url>
   cd fastapi_tts_project
   ```
2. 安装依赖：
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. 配置阿里云 TTS 的 API Key/Secret（在 main.py 中填写）。
4. 启动服务：
   ```bash
   uvicorn main:app --reload
   ```
5. 通过 API 上传对话文本，远程触发语音合成与循环播放。

## 备用说明
- 支持自定义音频间隔、循环次数等参数，可在 main.py 中调整。
- 详细接口文档与示例见后续补充。

## API 使用说明

### 1. 上传对话
- 接口：`POST /upload_dialogue`
- 参数：
  - `dialogue`（表单字段，支持两种格式）：
    - 纯文本（带“患者：”“医生：”前缀，每行一条）
    - 或结构化 JSON：`[{"role": "patient", "text": "..."}, {"role": "doctor", "text": "..."}]`
- 返回：`{"session_id": "1", "count": 2, ...}`
- 示例：
  ```bash
  curl -X POST "http://127.0.0.1:8000/upload_dialogue" -F 'dialogue=患者：你好\n医生：你好，有什么问题？'
  ```

### 2. 合成音频
- 接口：`POST /synthesize_audio`
- 参数：
  - `session_id`（字符串，上传对话返回的ID）
- 返回：`{"audio_files": [...], ...}`
- 示例：
  ```bash
  curl -X POST "http://127.0.0.1:8000/synthesize_audio" -F 'session_id=1'
  ```

### 3. 循环播放音频
- 接口：`POST /loop_playback`
- 参数：
  - `session_id`（字符串）
- 返回：`{"msg": ...}`
- 示例：
  ```bash
  curl -X POST "http://127.0.0.1:8000/loop_playback" -F 'session_id=1'
  ```

### 4. 停止循环播放
- 接口：`POST /stop_playback`
- 参数：
  - `session_id`（字符串）
- 返回：`{"msg": ...}`
- 示例：
  ```bash
  curl -X POST "http://127.0.0.1:8000/stop_playback" -F 'session_id=1'
  ```

## 依赖安装
- Python 3.8+
- pip install -r requirements.txt
- pip install simpleaudio  # 本地播放音频需

## 注意事项
- 需在 main.py 中填写阿里云 TTS 的 AccessKey、AppKey、Token。
- 服务器需有音频播放能力（如本地物理机）。
- 如需前端页面或更复杂的API安全控制，可自行扩展。
