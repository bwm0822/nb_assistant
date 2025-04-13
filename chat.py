
import modules.llm_tc as llm
import modules.recognise as sr
from modules.speech import text_to_speech
import winsound
import time

DEBUG = False
SPEECH = True
global event
event = None
hotword = ["川普",'習近平']  # 喚醒詞

def msg(message):
    print(message)
    # if SPEECH : text_to_speech(message[:50].strip())
    if SPEECH : text_to_speech(message)

def unit_test():
    while True:
        user_input = input("請輸入問題：")
        if user_input.lower() == 'exit':
            break
        elif user_input.lower() == 'clear':
            print("\033[H\033[J", end='')
        else:
            print(llm.main(user_input))

def pause(): 
    llm.pause()

def resume(): 
    llm.resume()

def clear(): 
    llm.clear()

def beepRec():
    winsound.Beep(500, 150)  # 頻率500Hz，持續150毫秒
    print("\033[32m請說...\033[0m")

def beepStop():
    winsound.Beep(800, 300)  # 頻率300Hz，持續300毫秒
    print("\033[31m待命...\033[0m")

def main():
    msg("主人，你好！我是你的小女僕...請叫人家的小名(川普、習進平)將小女僕喚醒喔...")
    while True:
        # 步驟1: 等待喚醒詞
        if not DEBUG: sr.hotword(hotword)
        else: input("按ENTER鍵開始")

        # 步驟2: 開始錄音5秒，並辨識語音
        pause()
        print("AI:")
        msg("主人，請說")
        beepRec()
        user_input = input() if DEBUG else sr.record(5)
        if user_input is None or user_input.strip() == "": resume(); beepStop(); continue

        # 步驟3: 將語音辨識內容輸入 LLM
        print("你:\n", user_input)
        ret = llm.main(user_input)

        type = ret.get('type', '')
        if type == 'end': return
        if type != 'thread': msg(ret.get('msg', ''))
        resume(); beepStop()

        

def test():
    beepRec()
    time.sleep(1)  # 等待1秒
    beepStop()

if __name__ == "__main__":
    main()
    # unit_test()
    # test()