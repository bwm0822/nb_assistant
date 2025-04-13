
import yt_dlp
import vlc
import time

global player,videos,playlist,index
player = None
videos = []
playlist = []
index = 0

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
        "default_search": "ytsearch5",  # 使用 YouTube 搜尋前5筆結果
        'quiet': True,   # 不顯示下載過多訊息
        'noplaylist': True,
    }

    # 執行搜尋
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)  # 只抓影片資訊

    # 取得搜尋結果
    print(f"搜尋關鍵字：{query}")
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
        playlist.append(f"{video['title']} - {seconds_to_hms(video['duration'])} - {size_mb:.2f} MB")

    return {"status":1, "content":playlist}  # 回傳搜尋結果

def play(video):
    # 只想播放 單一影片或音訊，不需要進階控制
    global player
    if video == '': return {"status":-1, "msg":"video 為空"}

    if player is None:
        player = vlc.MediaPlayer(video['url'])
    else:
        player.stop()
        media = vlc.Media(video['url'])
        player.set_media(media)
    player.play()
    return {"status":1, "msg":f"播放：{playlist[index]}"}

def play_multi(url):
    global player
    # 需要管理 多個播放器（如播放多個音訊或影片）
    instance = vlc.Instance("--no-xlib")  # 避免 GUI 錯誤
    player = instance.media_player_new()
    media = instance.media_new(url)
    player.set_media(media)
    player.play()
    print(f"正在播放：{url}")
    time.sleep(5)  # 播放幾秒後，避免程式立即結束
    return player

def search_and_play(query):
    search_result = search(query)  # 搜尋影片
    if search_result['status'] == -1:
        return search_result  # 如果搜尋失敗，直接回傳錯誤訊息
    show_playlist()  # 顯示搜尋結果
    video = videos[0]  # 取得第一個搜尋結果
    return play(video)  # 播放第一個搜尋結果
    # return play_all()  # 播放搜尋結果清單

def pause():
    if player is None: return {"status":-1, "msg":"播放器未開啟"}
    player.pause()
    return {"status":1, "msg":"暫停"}

def resume():
    if player is None: return {"status":-1, "msg":"播放器未開啟"}
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
    global index
    if player is None: return {"status":-1, "msg":"播放器未開啟"}
    if len(playlist) == 0: return {"status":-1, "msg":"播放清單為空"}
    index = (index - 1) % len(playlist)  # 循環播放
    video = videos[index] # 取得上一首影片資訊
    player.stop()  # 停止當前播放
    media = vlc.Media(video['url'])  # 取得上一首影片的媒體資訊
    player.set_media(media)  # 設定新的媒體
    player.play()  # 播放新的媒體
    return {"status":1, "msg":f"播放：{playlist[index]}"}

def next():
    # 這裡可以實現播放下一首音樂的邏輯
    global index
    if player is None: return {"status":-1, "msg":"播放器未開啟"}
    if len(playlist) == 0: return {"status":-1, "msg":"播放清單為空"}
    index = (index + 1) % len(playlist)  # 循環播放
    video = videos[index] # 取得下一首影片資訊
    player.stop()  # 停止當前播放
    media = vlc.Media(video['url'])  # 取得下一首影片的媒體資訊
    player.set_media(media)  # 設定新的媒體
    player.play()  # 播放新的媒體
    filesize = video.get('filesize', 0)  # 取得檔案大小
    if filesize == 0:
        filesize = video.get('filesize_approx', 0)  # 嘗試取得近似檔案大小
    return {"status":1, "msg":f"播放：{playlist[index]}"}

def forward(sceonds):
    # 將當前播放時間向前跳轉指定的秒數
    if player is None: return {"status":-1, "msg":"播放器未開啟"}
    try: seconds = int(sceonds)
    except: seconds = 10
    current_time = player.get_time() / 1000  # 轉換為秒
    print(f"當前時間：{current_time}秒")
    player.set_time(int((current_time + seconds) * 1000))  # 設定新的播放時間
    return {"status":1, "msg":f"快轉 {seconds}秒"}

def backward(sceonds):
    # 將當前播放時間向後跳轉指定的秒數
    if player is None: return {"status":-1, "msg":"播放器未開啟"}
    try: seconds = int(sceonds)
    except: seconds = 10
    current_time = player.get_time() / 1000  # 轉換為秒
    print(f"當前時間：{current_time}秒")
    player.set_time(int((current_time - seconds) * 1000))  # 設定新的播放時間
    return {"status":1, "msg":f"倒退 {seconds}秒"}

def volumeup(delta=20):
    # 將音量增加 20%
    if player is None: return {"status":-1, "msg":"播放器未開啟"}
    current_volume = player.audio_get_volume()  # 取得當前音量
    new_volume = min(current_volume + delta, 100)  # 限制在 0-100 範圍內
    player.audio_set_volume(new_volume)  # 設定新的音量
    return {"status":1, "msg":f"音量增加到 {new_volume}%"}

def volumedn(delta=20):
    # 將音量減少 20%
    if player is None: return {"status":-1, "msg":"播放器未開啟"}
    current_volume = player.audio_get_volume()  # 取得當前音量
    new_volume = max(current_volume - delta, 0)  # 限制在 0-100 範圍內
    player.audio_set_volume(new_volume)  # 設定新的音量
    return {"status":1, "msg":f"音量減少到 {new_volume}%"}

def volume(vol):
    # 設定音量，範圍 0-100
    if player is None: return {"status":-1, "msg":"播放器未開啟"}
    try:
        clamp = lambda s: max(0, min(100, int(s.strip("%")))) 
        vol = clamp(vol)
    except: vol = 50
    player.audio_set_volume(vol)
    return {"status":1, "msg":f"音量設為 {vol}%"}


def mute(on):
    if player is None: return {"status":-1, "msg":"播放器未開啟"}
    try: on = on.lower() not in {"false", "off", "0"}
    except: on = True
    player.audio_set_mute(on)  # 設定靜音狀態
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

def execute(cmd, args):
    global player
    arg = args[0] if len(args)>0 else ''
    match cmd:
        case "open": return open()
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



if __name__ == "__main__":
    unit_test()
