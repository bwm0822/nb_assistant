from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

#功能說明 : 開啟 YouTube 並搜尋影片

def open():
    # 設定 Chrome 選項
    options = Options()
    options.add_argument("--start-maximized")  # 最大化視窗
    options.add_argument("--disable-blink-features=AutomationControlled")  # 防止 YouTube 檢測
    #options.add_argument("--mute-audio")  # 靜音影片
    options.add_argument("--disable-popup-blocking")  # 禁止彈出視窗
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")

    # Path to your ChromeDriver
    service = Service('./chromedriver/chromedriver.exe')  # Replace with the actual path to your ChromeDriver

    # Initialize the WebDriver
    driver = webdriver.Chrome(service=service, options=options)

    # Open YouTube
    driver.get("https://www.youtube.com")
    return driver

def close(driver):
    # Close the WebDriver
    driver.quit()
    return None

def pause(driver):
    # Pause the video if it's playing
    print("暫停影片")

    driver.execute_script("document.querySelector('video').pause()")

    # play_button = driver.find_element(By.CLASS_NAME, "ytp-play-button")
    # title = play_button.get_attribute("title")
    # print(title)
    # play_button.click()  # 這次點擊是暫停


def resume(driver):
    print("撥放影片")
    driver.execute_script("document.querySelector('video').play()")


def next(driver):
    print("撥放下一部影片")
    driver.execute_script("document.querySelector('.ytp-next-button').click();")
    # try:
    #     next_button = driver.find_element(By.CLASS_NAME, "ytp-next-button")
    #     next_button.click()
    #     print("播放下一個影片")
    # except Exception as e:
    #     print(f"Error playing next video: {e}")

def forward(driver, args):
    try: sec = int(args[0])
    except: sec = 10
    print(f"快轉 {sec}秒")
    driver.execute_script(f"document.querySelector('video').currentTime += {sec}")

def backward(driver, args):
    try: sec = int(args[0])
    except: sec = 10
    print(f"倒退 {sec}秒")
    driver.execute_script(f"document.querySelector('video').currentTime -= {sec}")

def get_status(driver):
    if driver is None:
        print("Driver is not initialized.")
        return None
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
            print("影片正在播放！")
            return 1
        else:
            print("影片未播放或暫停！")
            return 0
    else:
        print("影片無法播放或尚未載入！")
        return -1
    
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


def search_and_play(driver, args):
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
        print(f"成功撥放: {query}")
    
    except Exception as e:
        print(f"Error locating or clicking the first video: {e}")


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