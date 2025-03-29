
import speech_recognition as sr

#功能說明 : 將語音轉成文字

r = sr.Recognizer()

def recognition():
    with sr.Microphone() as source:
        #print("你: ")
        r.adjust_for_ambient_noise(source, duration=1)  # 適應環境噪音
        audio = r.listen(source)

        try:
            command = r.recognize_google(audio, language="zh-TW")  # 語言設定為繁體中文
            print("語音辨識:", command)
            return command
        except sr.UnknownValueError:
            print("無法辨識語音，請再試一次。")
            return None
        except sr.RequestError:
            print("無法連線到 Google 語音服務，請檢查網路。")
            return None