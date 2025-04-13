
import speech_recognition as sr
import pyaudio
import wave
import io
import time
if __name__ == "__main__":
    from speech import text_to_speech
else:
    from modules.speech import text_to_speech

# 錄音參數 
CHUNK = 1024                # 每次讀取的音訊幀數
FORMAT = pyaudio.paInt16    # 音訊格式
CHANNELS = 1                # 單聲道  
RATE = 16000                # 取樣率

DEBUG = False

#功能說明 : 將語音轉成文字
r = sr.Recognizer()
# r.energy_threshold = 300 #（數值可調整，數值越高代表需要更大聲的輸入才會觸發語音辨識）。

global _t
_t = 0
def start(label='start'):
    global _t
    _t = time.time()
    debug(f"{label}:{_t:.2f}秒")

def dt(label):
    global _t
    t = time.time()
    debug(f"{label}:{t-_t:.2f}秒")
    _t = t

def debug(*args):
    if DEBUG: print(*args)

def hotword(hotwords, timeout=None):
    while True:
        with sr.Microphone() as source:
            try:
                # r.adjust_for_ambient_noise(source, duration=1)  # 適應環境噪音
                r.energy_threshold = 20000  # （數值可調整，數值越高代表需要更大聲的輸入才會觸發語音辨識）。    
                dt(f'hot0:(th:{r.energy_threshold})')
                audio = r.listen(source,timeout=timeout)  # 設定超時時間
                dt('hot1')
                command = r.recognize_google(audio, language="zh-TW")  # 語言設定為繁體中文
                dt('hot2')
                for word in hotwords:
                    if word == command:
                        return
            except sr.WaitTimeoutError:
                print("等待語音輸入超時，請再試一次。")
                dt('hot3')
            except sr.UnknownValueError:
                debug("無法辨識語音，請再試一次。")
                dt('hot3')
            except sr.RequestError:
                print("無法連線到 Google 語音服務，請檢查網路。")

def hotword_rec(hotwords, timeout=3):
    while True:
        command = record(timeout)  # 等待語音輸入
        for word in hotwords:
            if word == command:
                return

def listen(timeout=None):
    with sr.Microphone() as source:
        try:
            # r.adjust_for_ambient_noise(source, duration=1)  # 適應環境噪音
            r.energy_threshold = 300  # （數值可調整，數值越高代表需要更大聲的輸入才會觸發語音辨識）。    
            print(f"請說話...{r.energy_threshold:.2f}")      
            audio = r.listen(source,timeout=timeout)  # 設定超時時間
            command = r.recognize_google(audio, language="zh-TW")  # 語言設定為繁體中文
            return command
        except sr.WaitTimeoutError:
            print("等待語音輸入超時，請再試一次。")
            return None
        except sr.UnknownValueError:
            print("無法辨識語音，請再試一次。")
            # return None
        except sr.RequestError:
            print("無法連線到 Google 語音服務，請檢查網路。")
            return None
        
def record(seconds):
    dt('rec0')
    p, frames = microphone(seconds)  # 開啟麥克風錄音
    # wav = save2IO(p, frames)  # 儲存到 BytesIO
    wav = save2file(p, frames) # 儲存到檔案
    with sr.AudioFile(wav) as source:
        audio = r.record(source)
    try:
        dt('rec1')
        command = r.recognize_google(audio, language="zh-TW")  # 語言設定為繁體中文
        return command
    except sr.UnknownValueError:
        dt('rec2')
        debug("無法辨識語音，請再試一次。")
        return None
    except sr.RequestError:
        print("無法連線到 Google 語音服務，請檢查網路。")
        return None

def microphone(seconds):
    p = pyaudio.PyAudio()
    # 開啟錄音串流
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    frames = []
    for i in range(0, int(RATE / CHUNK * seconds)):
        data = stream.read(CHUNK)
        frames.append(data)
    # 停止錄音
    stream.stop_stream()
    stream.close()
    p.terminate()
    return p, frames

def save2file(p, frames, filename='record.wav'):
    # 儲存 WAV
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    return filename

def save2IO(p, frames):
    # 把音訊寫進記憶體 (BytesIO)，模擬一個 wav 檔
    audio_bytes = io.BytesIO()
    wf = wave.open(audio_bytes, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    audio_bytes.seek(0)
    return audio_bytes
    

# 單元測試
# 功能說明 : 測試語音辨識模組是否正常運作
def unit_test():
    while True:

        command = listen()
        if command: print("辨識結果:", command)
        else: print("辨識失敗，請再試一次。")

        # user_input = input("按 Enter 繼續測試, q 離開")
        # if user_input.lower() == "q":
        #     break

def unit_test_1():        
    start('hotword')
    print("請說熱詞...")
    while True:
        hotword(['川普','習近平'])
        text_to_speech("是的，主人")
        # dt('chk0')
        text = record(5)
        # dt('chk1')
        if text is None: continue
        text_to_speech(text)
        

# 測試語音辨識
if __name__ == "__main__":
    unit_test_1()

