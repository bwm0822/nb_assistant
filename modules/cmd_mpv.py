
import mpv
if __name__ == "__main__":
    from cmd_dlp import search
else:
    from modules.cmd_dlp import search

global player, playlist

player = None
playlist = []

def sexy_time_format(time_str: str) -> str:
    parts = time_str.split(":")
    parts = [int(p) for p in parts]

    if len(parts) == 1:
        seconds = parts[0]
        return f"{seconds}秒"
    elif len(parts) == 2:
        minutes, seconds = parts
        if minutes == 0:
            return f"{seconds}秒"
        return f"{minutes}分{seconds}秒"
    elif len(parts) == 3:
        hours, minutes, seconds = parts
        return f"{hours}小時{minutes}分{seconds}秒"
    else:
        return "格式太淫蕩，人家解釋不了呢😳"

def show_playlist():
    # 顯示目前的播放清單
    print("播放清單：")
    for i,item in enumerate(playlist):
        print(f"{i + 1}. {item['title']} ({item['duration']})")

def get_playinfo(index):
    title = playlist[index]['title'].strip()[:50]
    duration = sexy_time_format(playlist[index]['duration'])
    return f"{title} ({duration})"
    
def play():
    global player
    if player is None: 
        player = mpv.MPV(ytdl=True, idle=True,volume=80)
        player.loop_playlist = "inf"  # 無限循環播放清單
    # 把所有影片加進 playlist，用 append 模式
    for i, item in enumerate(playlist):
        if i == 0:
            player.command("loadfile", item['url'], "replace")  # 第一首歌，當作主曲目
        else:
            player.command("loadfile", item['url'], "append")   # 後面的乖乖排隊聽命

    # 開始從第一首播放！
    player.command("playlist-play-index", "0")
    return {"status":1, "msg":f"播放：{get_playinfo(0)}"}


def search_and_play(query):
    ret = search(query)  # 搜尋影片
    if ret['status'] == -1:
        return ret  # 如果搜尋失敗，直接回傳錯誤訊息
    global playlist, index
    playlist = ret['content']  # 取得搜尋結果
    if len(playlist) == 0:
        return {"status":-1, "msg":"找不到影片"}  # 回傳搜尋結果
    show_playlist()  # 顯示搜尋結果
    return play()  # 播放第一個搜尋結果

def pause():
    if player is None: return {"status":-1, "msg":"播放器未開啟"}
    player.pause = True
    return {"status":1, "msg":"暫停"}

def resume():
    if player is None: return {"status":-1, "msg":"播放器未開啟"}
    player.pause = False
    return {"status":1, "msg":"繼續播放"}

def close():
    global player
    if player is None: return {"status":-1, "msg":"播放器未開啟"}
    player.terminate()
    player = None
    return {"status":1, "msg":"播放器已關閉"}

def previous():
    # 這裡可以實現播放上一首音樂的邏輯
    if player is None: return {"status":-1, "msg":"播放器未開啟"}
    
    pos = player.playlist_pos  # 取得當前播放的索引
    index = pos - 1 if pos > 0 else len(playlist) - 1  # 如果到第一首，就回到最後一首
    player.command("playlist-prev", "force")
    return {"status":1, "msg":f"播放：{get_playinfo(index)}"}

def next():
    # 這裡可以實現播放下一首音樂的邏輯
    if player is None: return {"status":-1, "msg":"播放器未開啟"}

    pos = player.playlist_pos  # 取得當前播放的索引
    index = pos + 1 if pos < len(playlist) - 1 else 0  # 如果到最後一首，就回到第一首
    player.command("playlist-next", "force")

    return {"status":1, "msg":f"播放：{get_playinfo(index)}"}


def forward(sceonds):
    # 將當前播放時間向前跳轉指定的秒數
    if player is None: return {"status":-1, "msg":"播放器未開啟"}
    try: seconds = int(sceonds)
    except: seconds = 10
    player.command("seek", seconds, "relative")
    return {"status":1, "msg":f"快轉{seconds}秒"}

def backward(sceonds):
    # 將當前播放時間向後跳轉指定的秒數
    if player is None: return {"status":-1, "msg":"播放器未開啟"}
    try: seconds = int(sceonds)
    except: seconds = 10
    player.command("seek", -seconds, "relative")
    return {"status":1, "msg":f"倒退{seconds}秒"}

def volumeup(delta=20):
    # 將音量增加 20%
    if player is None: return {"status":-1, "msg":"播放器未開啟"}
    player.mute = False  # 取消靜音
    vol = int(min(player.volume + delta, 100))  # 限制在 0-100 範圍內
    player.volume = vol
    return {"status":1, "msg":f"音量增加到{vol}%"}

def volumedn(delta=20):
    # 將音量減少 20%
    if player is None: return {"status":-1, "msg":"播放器未開啟"}
    player.mute = False  # 取消靜音
    vol = int(max(player.volume - delta, 0))  # 限制在 0-100 範圍內
    player.volume = vol
    return {"status":1, "msg":f"音量減少到{vol}%"}

def volume(vol):
    # 設定音量，範圍 0-100
    if player is None: return {"status":-1, "msg":"播放器未開啟"}
    try:
        # clamp = lambda s: max(0, min(100, int(s.strip("%")))) 
        vol = int(max(0, min(int(vol), 100))) # 限制在 0-100 範圍內
    except Exception as e:
        print(f"音量轉換錯誤: {e}")
        vol = 50
    player.mute = False  # 取消靜音
    player.volume = vol
    return {"status":1, "msg":f"音量設為{vol}%"}

def get_volume():
    # 取得當前音量
    if player is None: return {"status":-1, "msg":"播放器未開啟"}
    return {"status":1, "msg":f"音量:{int(player.volume)}%"}

def mute(on):
    if player is None: return {"status":-1, "msg":"播放器未開啟"}
    # try: on = on.lower() not in {"false", "off", "0"}
    # except: on = True
    if isinstance(on, str):
        on = on.strip().lower() in ["true", "1", "yes", "y"]
    else:
        on = bool(on)  # 不是字串就照正常邏輯轉成布林值
    player.mute = on  # 設定靜音，True 為靜音，False 為取消靜音
    return {"status":1, "msg":f"{'靜音' if on else '取消靜音'}"}

def is_pause():
    if player is None: return False
    return player.pause


def execute_old(cmd, args=[]):
    global player
    arg = args[0] if len(args)>0 else ''
    match cmd:
        case "close": return close()
        case "pause": return pause()
        case "resume": return resume()
        case "previous": return previous()
        case "next": return next()
        case "forward": return forward(arg)
        case "backward": return backward(arg)
        case "volumeup": return volumeup()
        case "volumedn": return volumedn()
        case "volume": return volume(arg)
        case "mute": return mute(arg)
        case "play": return search_and_play(arg)
        case _: return {"status":-1,"msg":"無效的指令"}

def execute(cmd, *args, **kwargs):
    match cmd:
        case "close": return close()
        case "pause": return pause()
        case "resume": return resume()
        case "previous": resume(); return previous()
        case "next": resume(); return next()
        case "forward": resume(); return forward(args[0])
        case "backward": resume(); return backward(args[0])
        case "volumeup": resume(); return volumeup()
        case "volumedn": resume(); return volumedn()
        case "get_volume": resume(); return get_volume()
        case "volume": resume(); return volume(args[0])
        case "mute": return mute(args[0])
        case "play": return search_and_play(args[0])
        case _: return {"status":-1,"msg":"無效的指令"}

def tools():
    return [
        {   "type": "function",
            "function": {
                "name": "tool_play",
                "description": "播放音樂、看節目",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "音樂、節目的名稱",
                        }
                    },
                    "required": ["title"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "tool_pause",
                "description": "暫停音樂",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "tool_resume",
                "description": "繼續播放音樂",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "tool_close",
                "description": "關閉播放器",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "tool_next",
                "description": "播放下一個",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "tool_previous",
                "description": "播放上一個",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "tool_forward",
                "description": "快轉指定秒數",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "seconds": {
                            "type": "integer",
                            "description": "快轉的秒數",
                        }
                    },
                    "required": ["seconds"]
                }   
            }
        },
        {
            "type": "function",
            "function": {
                "name": "tool_backward",
                "description": "倒退指定秒數",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "seconds": {
                            "type": "integer",
                            "description": "倒退的秒數",
                        }
                    },
                    "required": ["seconds"]
                }
            }
        },
        {
            "type": "function",
                "function": {
                "name": 'tool_volume',
                'description': '設置音量',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'volume': {
                            'type': 'integer',
                            'description': '音量大小（0-100）',
                        }
                    },
                    'required': ['volume']
                }
            }
        },
        {
            "type": "function",
                "function": {
                "name": 'tool_get_volume',
                'description': '取得音量',
                'parameters': {
                    'type': 'object',
                    'properties': {},
                    'required': []
                }
            }
        },
        {
            "type": "function",
            "function": {
                'name': 'tool_mute',
                'description': '靜音或取消靜音',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'on': {
                            'type': 'boolean',
                            'description': '是否靜音（true/false）',
                        }
                    },
                    'required': ['on']
                }
            }
        },
        {
            "type": "function",
                "function": {
                'name': 'tool_volumeup',
                'description': '音量增強',
                'parameters': {
                    'type': 'object',
                    'properties': {},
                    'required': []
                }
            }
        },
        {
            "type": "function",
            "function": {
                'name': 'tool_volumedn',
                'description': '音量減少',
                'parameters': {
                    'type': 'object',
                    'properties': {},
                    'required': []
                }
            }
        },
    ]

# 單元測試
def unit_test():
    while True:
        user_input = input("請輸入指令和參數 (例如: play '關鍵字')，按 q 離開\n")
        if user_input.lower() == "q": break
        sps = user_input.strip().split()
        print(sps, len(sps))
        if len(sps) > 0: cmd = sps[0]; args = sps[1:]
        else: cmd=''; args=[]
        print(f"指令: {cmd}, 參數: {args}")
        # print(execute(cmd, args))

        print(execute(cmd, args[0] if len(args)>0 else ''))



if __name__ == "__main__":
    unit_test()
