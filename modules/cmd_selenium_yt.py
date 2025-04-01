from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time

#功能說明 : 開啟 YouTube 並搜尋影片

global driver
driver = None

def open():
    global driver
    # 設定 Chrome 選項
    options = Options()
    options.add_argument("--start-maximized")  # 最大化視窗
    options.add_argument("--disable-blink-features=AutomationControlled")  # 防止 YouTube 檢測
    #options.add_argument("--mute-audio")  # 靜音影片
    options.add_argument("--disable-popup-blocking")  # 禁止彈出視窗
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")

    # # Path to your ChromeDriver
    # service = Service('./chromedriver/chromedriver.exe')  # Replace with the actual path to your ChromeDriver
    # # Initialize the WebDriver
    # driver = webdriver.Chrome(service=service, options=options)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Open YouTube
    driver.get("https://www.youtube.com")
    return {"status":1, "text":"開啟 youtube"}

def close():
    global driver
    if driver is None: return {"status":-1, "text":"youtube 未開啟"}
    driver.quit()
    driver = None
    return {"status":1, "text":"關閉 youtube"}

def pause():
    if driver is None: return {"status":-1, "text":"youtube 未開啟"}
    driver.execute_script("document.querySelector('video').pause()")
    return {"status":1, "text":"暫停"}

def resume():
    if driver is None: return {"status":-1, "text":"youtube 未開啟"}
    driver.execute_script("document.querySelector('video').play()")
    return {"status":1, "text":"繼續"}

def next():
    if driver is None: return {"status":-1, "text":"youtube 未開啟"}
    driver.execute_script("document.querySelector('.ytp-next-button').click();")
    return {"status":1, "text":"下一個"}

def forward(args):
    if driver is None: return {"status":-1, "text":"youtube 未開啟"}
    try: sec = int(args[0])
    except: sec = 10
    driver.execute_script(f"document.querySelector('video').currentTime += {sec}")
    return {"status":1, "text":f"快轉 {sec}秒"}

def backward(args):
    if driver is None: return {"status":-1, "text":"youtube 未開啟"}
    try: sec = int(args[0])
    except: sec = 10
    driver.execute_script(f"document.querySelector('video').currentTime -= {sec}")
    return {"status":1, "text":f"倒退 {sec}秒"}

## 設定音量
## 參數範圍 0% - 100%
def volume(args):   
    if driver is None: return {"status":-1, "text":"youtube 未開啟"}
    try:
        convert_percent = lambda s: max(0, min(1, float(s.strip("%")) / 100)) 
        vol = convert_percent(args[0])
    except: vol = 0.5
    # 獲取 video 元素
    video = driver.find_element(By.TAG_NAME, "video")
    # 使用 JavaScript 設定音量 (範圍 0.0 - 1.0)
    volume = driver.execute_script("return document.querySelector('video').volume")
    print(f"目前音量: {volume:.2f}")
    driver.execute_script(f"arguments[0].volume = {vol};", video)  # 設為 50% 音量
    return {"status":1, "text":f"音量設為 {vol*100:.0f}%"}

def mute(args):
    if driver is None: return {"status":-1, "text":"youtube 未開啟"}
    # 獲取 video 元素
    try:
        on = args[0].lower() not in {"false", "off", "0"}
    except:
        on = True
    video = driver.find_element(By.TAG_NAME, "video")
    # 使用 JavaScript 設定音量為 0
    driver.execute_script(f"arguments[0].muted = {'true' if on else 'false'};", video)  # 靜音
    return {"status":1, "text":f"{'靜音' if on else '取消靜音'}"}


def get_status():
    if driver is None: return {"status":-1, "text":"youtube 未開啟"}
    # Check if the video element is present
    is_playable = driver.execute_script("""
        let video = document.querySelector('video');
        return video && video.readyState === 4;
    """)

    if is_playable:
        is_playing = driver.execute_script("""
            let video = document.querySelector('video');
            return video && !video.paused;
        """)
        if is_playing:
            return {"status":1, "text":"影片正在播放！"}
        else:
            return {"status":-1, "text":"影片未播放或暫停！"}
    else:
        return {"status":-1, "text":"影片無法播放或尚未載入！"}
    

def search_and_play(args):
    if driver is None: return {"status":-1, "text":"youtube 未開啟"}
    try:
        query = args[0].strip()
        if query == "":
            raise ValueError("搜尋關鍵字為空")
        print(f"搜尋關鍵字: {query}")
    except IndexError:
        return {"status":-1, "text":"搜尋關鍵字為空"}
    except ValueError as e:
        return {"status":-1, "text":e}

    # 刷新頁面，確保每次搜尋都從新的頁面開始
    driver.refresh()

    # 等待頁面加載完成
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.NAME, "search_query"))
    )

    # 等待搜尋框加載（刷新後重新抓取搜尋框）
    search_box = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.NAME, "search_query"))
    )

    # 清除搜尋框中的舊關鍵字
    search_box = driver.find_element(By.NAME, "search_query")
    search_box.clear()
    search_box.send_keys(query)  # 輸入新的搜尋關鍵字
    search_box.submit()  # 提交搜尋

    try:
        # 等待搜尋結果加載並定位到第一個影片
        first_video = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'ytd-video-renderer a#thumbnail'))
        )
        
        # 滾動到第一個視頻元素，並確保視頻元素可見
        # driver.execute_script("document.querySelector('video').scrollIntoView(true);")
        driver.execute_script("arguments[0].scrollIntoView(true);", first_video)
        
        # 使用 document.querySelector 查找並點擊 video 元素
        #driver.execute_script("document.querySelector('video').click();")
        driver.execute_script("arguments[0].click();", first_video)
        return {"status":1, "text":f"成功撥放: {query}"}
    except Exception as e:
        return {"status":-1, "text":e}

def execute(cmd, args):
    global driver
    match cmd:
        case "open": return open()
        case "close": return close()
        case "pause": return pause()
        case "resume": return resume()
        case "next": return next()
        case "forward": return forward(args)
        case "backward": return backward(args)
        case "volume": return volume(args)
        case "mute": return mute(args)
        case "play":
            if driver is None: open() 
            return search_and_play(args)
        case "status": return get_status()
        case _: return {"status":-1,"text":"無效的指令"}


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
    















def search_and_play_bak(driver, args):
    try:
        query = args[0]
        print(f"搜尋關鍵字: {query}")
        if query.strip() == "":
            raise ValueError("搜尋關鍵字為空")
    except:
        print("搜尋關鍵字為空")
        return
    
    print(f"搜尋: {query}")
    # 定位到搜尋框並搜尋歌曲
    search_box = driver.find_element("name", "search_query")
    search_box.send_keys("Your Song Name Here")  # 輸入歌曲名稱
    search_box.send_keys(Keys.RETURN)  # 按下回車鍵搜尋

    # 等待搜尋結果加載
    time.sleep(3)

    # 點擊第一個搜尋結果
    first_result = driver.find_element("id", "video-title")
    first_result.click()


def search_and_play_1(driver, args):
    # Find the search box and enter the query
    try:
        query = args[0]
        print(f"搜尋關鍵字: {query}")
        if query.strip() == "":
            raise ValueError("搜尋關鍵字為空")
    except:
        print("搜尋關鍵字為空")
        return
    print(f"搜尋: {query}")
    search_box = driver.find_element(By.NAME, "search_query")
    search_box.clear()  # Clear the search box if needed
    search_box.send_keys(query)
    search_box.submit()

    try:
        # Wait for the results to load and locate the first video
        first_video = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'ytd-video-renderer a#thumbnail'))
        )
        # Scroll the element into view
        driver.execute_script("arguments[0].scrollIntoView(true);", first_video)
        # Use JavaScript to click the element to avoid interception
        driver.execute_script("arguments[0].click();", first_video)
    except Exception as e:
        print(f"Error locating or clicking the first video: {e}")





def search_and_play_2(driver, args):
    try:
        query = args[0].strip()
        if query == "":
            raise ValueError("搜尋關鍵字為空")
        print(f"搜尋關鍵字: {query}")
    except IndexError:
        print("搜尋關鍵字為空")
        return
    except ValueError as e:
        print(e)
        return

    # 搜尋
    search_box = driver.find_element(By.NAME, "search_query")
    search_box.clear()  # 清除搜尋框中的任何文字
    search_box.send_keys(query)  # 輸入搜尋關鍵字
    search_box.submit()  # 提交搜尋

    try:
        # 等待搜尋結果加載並定位到第一個影片
        first_video = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'ytd-video-renderer a#thumbnail'))
        )
        
        # 滾動到視頻元素，保證它可見
        driver.execute_script("arguments[0].scrollIntoView(true);", first_video)
        
        # 使用 document.querySelector 查找並點擊 video 元素
        driver.execute_script("document.querySelector('video').click();")
        print(f"成功撥放: {query}")
    
    except Exception as e:
        print(f"Error locating or clicking the first video: {e}")