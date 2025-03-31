
import speech_recognition as sr
import webrtcvad
import collections
import pyaudio
import wave

r = sr.Recognizer()
vad = webrtcvad.Vad(2)  # 設定 WebRTC 降噪等級 (0~3，數字越大越嚴格)

# 錄音參數
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000  # WebRTC 推薦 16kHz
FRAME_DURATION = 30  # 每個 frame 長度（ms）
FRAME_SIZE = int(RATE * FRAME_DURATION / 1000)  # 480 取樣點（16kHz）
BUFFER_SIZE = 10  # 10 個 frame 緩衝區

def record_audio():
    """使用 WebRTC 過濾背景噪音並錄音"""
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=FRAME_SIZE)

    # print("請開始說話...")
    frames = collections.deque(maxlen=BUFFER_SIZE)
    speech_frames = []

    try:
        while True:
            frame = stream.read(FRAME_SIZE, exception_on_overflow=False)
            frames.append(frame)

            if vad.is_speech(frame, RATE):  # 檢測語音
                speech_frames.extend(frames)
                frames.clear()
            elif speech_frames:
                break  # 如果語音結束，停止錄音

    except KeyboardInterrupt:
        print("錄音結束")

    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()

    # 存成 WAV 檔案
    with wave.open("filtered_audio.wav", "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b"".join(speech_frames))

    return "filtered_audio.wav"

def recognition():
    """辨識 WebRTC 降噪後的語音"""
    audio_file = record_audio()

    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)

    try:
        command = r.recognize_google(audio, language="zh-TW")  # 繁體中文
        # print("語音辨識:", command)
        return command
    except sr.UnknownValueError:
        print("無法辨識語音，請再試一次。")
        return None
    except sr.RequestError:
        print("無法連線到 Google 語音服務，請檢查網路。")
        return None

# 單元測試
# 功能說明 : 測試語音辨識模組是否正常運作
def unit_test():
    while True:
        print("請說話...")    
        command = recognition()
        if command:
            print("辨識結果:", command)
        else:
            print("辨識失敗，請再試一次。")

        user_input = input("按 Enter 繼續測試, q 離開")
        if user_input.lower() == "q":
            break


# 測試語音辨識
if __name__ == "__main__":
    unit_test()