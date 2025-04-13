from yt_dlp import YoutubeDL

def seconds_to_hms(seconds):
    # float() 轉成浮點數，是為了避免 seconds 為浮點數字串(如:'123.0')時，直接用 int() 會出錯
    # print(f"seconds: {seconds}")
    try: seconds = int(float(seconds))  # 確保是整數
    except Exception as e:  # 捕捉所有例外
        print(f"Error:{e}"); seconds = 0
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0: hms = f"{hours}:{minutes:02}:{seconds:02}"
    else: hms = f"{minutes}:{seconds:02}"  # 如果沒有小時，就顯示 MM:SS
    # print(f"duration: {hms}")
    return hms

def search(query):
    if query == '': return {"status":-1, "msg":"搜尋關鍵字為空"}

    ydl_opts = {
        'format': 'best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch5',  # 搜尋前5個
        'extract_flat': True,          # ❌ 不要 flat，才能拿到真正可播放的 URL
    }

    search_url = f"ytsearch5:{query}" 
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(search_url, download=False)
        # 若是 playlist，就取 entries
        if info.get('_type') == 'playlist':
            entries = info['entries']
        else:
            entries = [info]

    playlist=[]
    for entry in entries:
        url = entry.get('url', '')
        title = entry.get('title','')
        duration = entry.get('duration','')
        playlist.append({"url": url, "title": title, "duration": seconds_to_hms(duration)})
        # filesize = entry.get('filesize','')
        # filesize_approx = entry.get('filesize_approx','')
        
    # urls = [entry['url'] for entry in entries if 'url' in entry]
    return {'status':1, 'content':playlist}


def download(query):
    # 使用 yt-dlp 進行 YouTube 搜尋
    search_url = f"ytsearch:{query}"

    # 設定 yt-dlp 下載選項
    ydl_opts = {
        'format': 'best',  # 下載最佳畫質
        # 'format': 'bestaudio',  # ✅ 只選擇最佳音訊
        'outtmpl': '%(title)s.%(ext)s',  # 影片標題作為檔名
        'noplaylist': True,  # 不下載播放清單
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(search_url, download=False)  # 搜尋但不下載
        if 'entries' in info and len(info['entries']) > 0:
            first_video = info['entries'][0]  # 取得第一個影片資訊
            print(f"找到影片: {first_video['title']} ({first_video['webpage_url']})")

            # 下載該影片
            ydl.download([first_video['webpage_url']])

    print("下載完成！")

def unit_test():
     while True:
        user_input = input("請輸入指令和參數(search '關鍵字',q:離開)\n")
        if user_input.lower() == "q": break
        cmds = user_input.strip().split()
        print(f"指令: {cmds[0]}, 參數: {cmds[1]}")
        match cmds[0]:
            case "search":
                print(search(cmds[1]))
            case "download":
                download(cmds[1])
            case _:
                print("無效的指令")


if __name__ == "__main__":
    unit_test()