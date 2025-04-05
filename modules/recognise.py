
import speech_recognition as sr

#功能說明 : 將語音轉成文字

r = sr.Recognizer()
# r.energy_threshold = 300 #（數值可調整，數值越高代表需要更大聲的輸入才會觸發語音辨識）。


def recognition(timeout=None):
    with sr.Microphone() as source:
        try:
            r.adjust_for_ambient_noise(source, duration=1)  # 適應環境噪音
            audio = r.listen(source,timeout=timeout)  # 設定超時時間
            command = r.recognize_google(audio, language="zh-TW")  # 語言設定為繁體中文
            # print("語音辨識:", command)
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

