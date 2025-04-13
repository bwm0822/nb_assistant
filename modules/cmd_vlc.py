
import yt_dlp
import vlc
import time

global player,videos,playlist,index,media_list

instance = vlc.Instance()   # 建立 VLC 環境
player = None
videos = []
playlist = []
index = 0
media_list = None

def seconds_to_hms(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0: return f"{hours}:{minutes:02}:{seconds:02}"
    else: return f"{minutes}:{seconds:02}"  # 如果沒有小時，就顯示 MM:SS

def show_playlist():
    # 顯示目前的播放清單
    print("播放清單：")
    for i,item in enumerate(playlist):
        print(f"{i + 1}. {item}")

def search(query):
    # 設定 yt-dlp 參數
    if query == '': return {"status":-1, "msg":"搜尋關鍵字為空"}

    ydl_opts = {
        'format': 'b',  # 選擇最佳預合併格式
        # 'format': 'bestaudio',  # ✅ 只選擇最佳音訊
        # "default_search": "ytsearch5",  # 使用 YouTube 搜尋前5筆結果
        'quiet': True,   # 不顯示下載過多訊息
        'noplaylist': True,
        # 'socket_timeout': 10,  # 最多等10秒
        'extract_flat': True,  # 💥 關鍵設定！
    }

    # 執行搜尋
    print(f"搜尋關鍵字：{query}")
    # search_url = f"ytsearchdate5:{query}"
    search_url = f"ytsearch5:{query}" # 搜尋 周杰倫 會有卡住的問題
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_url, download=False)  # 只抓影片資訊
            # entries = info.get("entries", [])

            # # 過濾掉預告片（Premiere）影片
            # public_entries = [entry for entry in entries if not entry.get('premiere', False)]
    except Exception as e:
        print("🥵 錯誤發生啦：", e)
        return {"status":-1, "msg":e}

    # 取得搜尋結果
    global videos, playlist, index
    videos = info['entries']  # 儲存搜尋結果
    index = 0  # 重設索引
    if not videos:
        return {"status":-1, "msg":"找不到影片"}  # 回傳搜尋結果

    playlist = []  # 儲存選單
    for i, video in enumerate(videos):
        size = video.get('filesize', 0)  # 取得檔案大小
        if size == 0: size = video.get('filesize_approx', 0)
        size_mb = size / 1024 / 1024 if size else 0  # 避免 NoneType 錯誤
        playlist.append(f"{video['title']} - {seconds_to_hms(video.get('duration',0))} - {size_mb:.2f} MB")

    return {"status":1, "content":playlist}  # 回傳搜尋結果

    
def play():
    global player, media_list, index

    if media_list: media_list.release()
    media_list = instance.media_list_new()

    for video in videos:
        media = instance.media_new(video['url'])
        media_list.add_media(media)

    # 播放
    if player is None: player = instance.media_list_player_new()
    else: player.stop()
    player.set_media_list(media_list)
    player.play()
    index = 0

    return {"status":1, "msg":f"播放：{playlist[index]}"}


def search_and_play(query):
    search_result = search(query)  # 搜尋影片
    if search_result['status'] == -1:
        return search_result  # 如果搜尋失敗，直接回傳錯誤訊息
    show_playlist()  # 顯示搜尋結果
    return play()  # 播放第一個搜尋結果

def pause():
    if player is None: return {"status":-1, "msg":"播放器未開啟"}
    if player.is_playing():
        player.pause()
    return {"status":1, "msg":"暫停"}

def resume():
    if player is None: return {"status":-1, "msg":"播放器未開啟"}
    if not player.is_playing():
        player.play()
    return {"status":1, "msg":"繼續播放"}

def close():
    global player
    if player is None: return {"status":-1, "msg":"播放器未開啟"}
    player.stop()
    player.release()  # 釋放資源
    player = None
    return {"status":1, "msg":"播放器已關閉"}

def previous():
    # 這裡可以實現播放上一首音樂的邏輯
    if player is None: return {"status":-1, "msg":"播放器未開啟"}
    
    global index
    pre_mrl = get_mrl()
    player.previous()  # 播放下一首音樂
    time.sleep(0.5)
    next_mrl = get_mrl()

    if pre_mrl != next_mrl:
        index = max(index - 1, 0)  # 確保索引不超出範圍
        print('播放上一個')
    else:
        print('播放當的')
    return {"status":1, "msg":f"播放：{playlist[index]}"}

def next():
    # 這裡可以實現播放下一首音樂的邏輯
    if player is None: return {"status":-1, "msg":"播放器未開啟"}

    global index    
    pre_mrl = get_mrl()
    player.next()  # 播放下一首音樂
    time.sleep(0.5)
    next_mrl = get_mrl()

    if pre_mrl != next_mrl:
        index = (index + 1) % len(playlist)  # 確保索引不超出範圍
        print('播放下一個')
    else:
        print('播放當前的')

    return {"status":1, "msg":f"播放：{playlist[index]}"}

def get_mrl():
    media_player = player.get_media_player()
    media = media_player.get_media()
    return media.get_mrl()

def forward(sceonds):
    # 將當前播放時間向前跳轉指定的秒數
    if player is None: return {"status":-1, "msg":"播放器未開啟"}
    try: seconds = int(sceonds)
    except: seconds = 10
    media_player = player.get_media_player()
    current_time = media_player.get_time()
    new_time = current_time + seconds * 1000  # 換算為毫秒
    media_player.set_time(new_time)
    return {"status":1, "msg":f"快轉 {seconds}秒"}

def backward(sceonds):
    # 將當前播放時間向後跳轉指定的秒數
    if player is None: return {"status":-1, "msg":"播放器未開啟"}
    try: seconds = int(sceonds)
    except: seconds = 10
    media_player = player.get_media_player()
    current_time = media_player.get_time()
    new_time = max(current_time - seconds * 1000, 0)
    media_player.set_time(new_time)
    return {"status":1, "msg":f"倒退 {seconds}秒"}

def volumeup(delta=20):
    # 將音量增加 20%
    if player is None: return {"status":-1, "msg":"播放器未開啟"}
    media_player = player.get_media_player()
    media_player.audio_set_mute(False)  # 取消靜音
    current_volume = media_player.audio_get_volume()  # 取得當前音量
    new_volume = min(current_volume + delta, 100)  # 限制在 0-100 範圍內
    media_player.audio_set_volume(new_volume)  # 設定新的音量
    return {"status":1, "msg":f"音量增加到 {new_volume}%"}

def volumedn(delta=20):
    # 將音量減少 20%
    if player is None: return {"status":-1, "msg":"播放器未開啟"}
    media_player = player.get_media_player()
    media_player.audio_set_mute(False)  # 取消靜音
    current_volume = media_player.audio_get_volume()  # 取得當前音量
    new_volume = max(current_volume - delta, 0)  # 限制在 0-100 範圍內
    media_player.audio_set_volume(new_volume)  # 設定新的音量
    return {"status":1, "msg":f"音量減少到 {new_volume}%"}

def volume(vol):
    # 設定音量，範圍 0-100
    if player is None: return {"status":-1, "msg":"播放器未開啟"}
    try:
        # clamp = lambda s: max(0, min(100, int(s.strip("%")))) 
        vol = max(0, min(100, vol)) # 限制在 0-100 範圍內
    except: 
        vol = 50
    media_player = player.get_media_player()
    media_player.audio_set_mute(False)  # 取消靜音
    media_player.audio_set_volume(vol)
    return {"status":1, "msg":f"音量設為 {vol}%"}

def get_volume():
    # 取得當前音量
    if player is None: return {"status":-1, "msg":"播放器未開啟"}
    media_player = player.get_media_player()
    current_volume = media_player.audio_get_volume()  # 取得當前音量
    return {"status":1, "msg":f"音量:{current_volume}%"}

def mute(on):
    if player is None: return {"status":-1, "msg":"播放器未開啟"}
    # try: on = on.lower() not in {"false", "off", "0"}
    # except: on = True
    if isinstance(on, str):
        on = on.strip().lower() in ["true", "1", "yes", "y"]
    else:
        on = bool(on)  # 不是字串就照正常邏輯轉成布林值
    media_player = player.get_media_player()
    media_player.audio_set_mute(on)  # 設定靜音狀態
    return {"status":1, "msg":f"{'靜音' if on else '取消靜音'}"}


def download(search_query):
    # 使用 yt-dlp 進行 YouTube 搜尋
    search_url = f"ytsearch:{search_query}"

    # 設定 yt-dlp 下載選項
    ydl_opts = {
        'format': 'best',  # 下載最佳畫質
        # 'format': 'bestaudio',  # ✅ 只選擇最佳音訊
        'outtmpl': '%(title)s.%(ext)s',  # 影片標題作為檔名
        'noplaylist': True,  # 不下載播放清單
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(search_url, download=False)  # 搜尋但不下載
        if 'entries' in info and len(info['entries']) > 0:
            first_video = info['entries'][0]  # 取得第一個影片資訊
            print(f"找到影片: {first_video['title']} ({first_video['webpage_url']})")

            # 下載該影片
            ydl.download([first_video['webpage_url']])

    print("下載完成！")


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
    global player
    match cmd:
        case "close": return close()
        case "pause": return pause()
        case "resume": return resume()
        case "previous": resume(); return previous()
        case "next": return next()
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
                "name": "play",
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
                "name": "pause",
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
                "name": "resume",
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
                "name": "close",
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
                "name": "next",
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
                "name": "previous",
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
                "name": "forward",
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
                "name": "backward",
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
                "name": 'volume',
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
                "name": 'get_volume',
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
                'name': 'mute',
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
                'name': 'volumeup',
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
                'name': 'volumedn',
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

        print(execute(cmd, args))
        # print(execute_1(cmd, args[0]))



if __name__ == "__main__":
    unit_test()
