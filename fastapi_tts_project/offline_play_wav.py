import time
import os
from pydub import AudioSegment
from pydub.playback import play
from pynput import keyboard   
import threading

# 录音文件夹路径
audio_dir = os.path.dirname(os.path.abspath(__file__))  # 脚本所在目录
#audio_dir = "/Users/ssmac/Downloads/dialogue_wav/"  

# 分组，按文件名顺序
groups = [
    ['1.wav', '2.wav', '3.wav', '4.wav'],
    ['5.wav', '6.wav', '7.wav'],
    ['8.wav', '9.wav', '10.wav'],
    ['11.wav', '12.wav', '13.wav'],
    ['14.wav', '15.wav']
]

def play_audio_group(group):
    for idx, filename in enumerate(group):
        filepath = os.path.join(audio_dir, filename)
        if os.path.exists(filepath):
            print(f"Playing {filepath}")
            audio = AudioSegment.from_file(filepath)
            play(audio)
        else:
            print(f"File not found: {filepath}")
        # 组内录音间隔1秒，最后一个不需要
        if idx < len(group) - 1:
            time.sleep(1)

if __name__ == "__main__":
    while True:
        for group_idx, group in enumerate(groups):
            play_audio_group(group)
            # 组间隔2秒，最后一组不需要
            if group_idx < len(groups) - 1:
                time.sleep(2)
        # 每一轮全部播放完后，停顿6秒
        time.sleep(5)


'''
#备用功能代码：
#1. 设置“指定两个音频之间”的时间间隔
#假设要让a.wav和b.wav之间间隔5秒，其他默认1秒，可以这样实现：
# 假设 group = ['a.wav', 'b.wav', 'c.wav']
for idx, filename in enumerate(group):
    # ...播放代码...
    if idx < len(group) - 1:
        # 指定a.wav和b.wav之间5秒，其他1秒
        if filename == 'a.wav' and group[idx + 1] == 'b.wav':
            time.sleep(5)
        else:
            time.sleep(1)

2. 手动输入全部音频各自间隔（用数组设定）
假设有5个音频，想让第1和第2之间间隔2秒，第2和第3之间3秒，第3和第4之间1秒，第4和第5之间4秒：
group = ['1.wav', '2.wav', '3.wav', '4.wav', '5.wav']
intervals = [2, 3, 1, 4]  # 间隔数比音频数少1

for idx, filename in enumerate(group):
    # ...播放代码...
    if idx < len(group) - 1:
        time.sleep(intervals[idx])
'''