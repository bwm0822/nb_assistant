import ollama
import re
import modules.cmd_selenium_yt as cmd_yt
# import modules.recognise as sr
import modules.recognise_webrtc as sr
from modules.speech import text_to_speech
import json

LLM_MODEL_NAME = "llama3.2"

news = """
緬甸強震引爆災情 電子五哥東南亞廠區均安 - 自由財經
即時
熱門
政治
財富自由
軍武
社會
生活
健康
國際
地方
蒐奇
影音
財經
娛樂
汽車
時尚
體育
3 C
評論
藝文
玩咖
食譜
地產
專區
TAIPEI TIMES
求職
爆
Search
自由電子報
自由財經
財經首頁
財經即時
財經政策
國際財經
證券產業
房產資訊
財經週報
基金查詢
投資理財
粉絲團
自由影音
即時
熱門
政治
軍武
社會
生活
健康
國際
地方
蒐奇
財富自由
財經
娛樂
藝文
汽車
時尚
體育
3 C
評論
玩咖
食譜
地產
專區
服務
自由電子報 APP
自由電子報粉絲團
自由電子報 Line
自由電子報 X
熱門新訊
財經即時
Breakingnews
財經政策
Strategy
影音專區
video
國際財經
International
證券產業
Securities
房產資訊
Estate
財經週報
Weeklybiz
基金查詢
Fund
投資理財
Investment
新聞查詢
Search
基金查詢
Search
Search
財經
>
證券產業
緬甸強震引爆災情 電子五哥東南亞廠區均安
2025/03/29 08:05
緬甸於週五中午12時50分發生芮氏規模7.7、震源深度僅10公里的劇烈強震，緊接著12分鐘又發生芮氏規模6.7、震源深度同樣只有10公里的餘震，兩起極淺層地震摧毀當地多幢建物。（美聯社）
〔記者方韋傑／台北報導〕緬甸週五（28日）中午發生劇烈強震，引發嚴重災情，地震波還引發鄰近的泰國曼谷當地高樓倒塌，整個東南亞局部地區甚至都能感受到搖晃，對此，電子五哥廣達（2382）、緯創（3231）、英業達（2356）、仁寶（2324）、和碩（4938）位於東南亞的各個廠區皆回報一切均安、正常運作。
廣達目前於泰國春武里府保稅區設有伺服器表面黏著（SMT）產線，緊鄰集團旗下廣明（6188）的自動化製造基地，在此次緬甸強震發生之後，並未影響工廠運行；而英業達則將泰國廠房設在北欖府，用於生產伺服器與筆電，管理層表示，由於震央所在地與廠區仍有相當程度的距離，「一切安好」。
請繼續往下閱讀...
仁寶近年持續擴大營運佈局，與關係企業金寶（2312）保持密切合作，而旗下泰金寶-DR（9105）位於泰國碧武里、馬哈差的廠區，以及設於曼谷的辦公室皆在緬甸強震過後維持正常運作，仁寶越南廠區也未受影響，至於緯創位於越南河內的消費性電子、網通產品工廠也同樣維持正常運作。
此外，和碩設於越南海防的廠區，以及位在印尼巴淡島的工廠，由於距離震央數千公里，儘管兩個地區的台商在緬甸強震發生當下仍有感受到些許搖晃，但並未影響所在地的供應鏈運行。
根據美國地質研究所（USGS）數據顯示，緬甸於週五中午12時50分發生芮氏規模7.7、震源深度僅10公里的劇烈強震，緊接著大約12分鐘後又發生芮氏規模6.7、震源深度同樣只有10公里的餘震，兩起極淺層地震摧毀當地多幢建物，當地軍政府釋出的訊息顯示，事故至少已造成144人死亡，目前正積極尋求國際社會援助救災行動。
一手掌握經濟脈動
點我訂閱自由財經Youtube頻道
不用抽 不用搶 現在用APP看新聞 保證天天中獎
點我下載APP
按我看活動辦法
相關新聞
今日熱門新聞
看更多！請加入自由財經粉絲團
網友回應
基金查詢
more
進階查詢 +
熱門新訊
more
自行車美學與科技結合 隱形冠軍「天心工業」擴大投資台中
SANLUX 台灣三洋健康冷氣 速捷淨 快拆好清理 健康好呼吸
高科大舉辦航太與低軌衛星研討會 助推台灣太空產業研發升級
三竹資訊獲ISO/IEC 27001資安驗證 保障客戶資訊安全
注目新聞
財經即時
財經政策
國際財經
證券產業
房產資訊
財經週報
基金查詢
投資理財
自由時報版權所有不得轉載
© 2025 The Liberty Times. All Rights Reserved.
"""

prompt_main = """
你是一個指令分析器，根據你收到的訊息，轉換成
forward backward resume pause next play close query chat 的指令，
轉換規則，指令格式如下：

1. 訊息: 快轉       指令格式:  forward(時間轉成秒數，沒有時間則設成10)
    範例:
    快轉            指令格式:   forward(10)
    快轉 時間       指令格式:   forward(時間轉成秒數)

2. 訊息: 倒轉       指令格式:   backward(時間轉成秒數，沒有時間則設成10)
    範例:
    倒轉            backward(10)
    倒轉 時間       backward(時間轉成秒數)

3. 訊息: 繼續       指令格式: resume()
4. 訊息: 暫停       指令格式: pause()
5. 訊息: 下一個     指令格式: next()

6. 訊息: 搜尋 關鍵字    指令格式:   play(關鍵字)
   訊息: 搜尋           指令格式:   query(請問要搜尋什麼)
    範例:
    搜尋抒情歌      play(抒情歌)
    搜尋            query(請問要搜尋什麼)

7. 敘述: 聽\撥歌\撥放 關鍵字   指令格式:    play(關鍵字)
   敘述: 聽\撥歌\撥放         指令格式:     query(請問要撥的歌)
    範例:
    聽伍佰的歌      play(伍佰的歌)
    聽              query(請問要聽什麼)

8. 訊息: 看\我想看 關鍵字     指令格式:     play(關鍵字)
   訊息: 看\我想看            指令格式:     query(請問要看什麼)
   範例:
    我想看新聞      play(新聞)
    我想看          query(請問要看什麼)

9. 訊息: 關閉               指令格式:   close()

10. 其他無法識別的指令，天氣、人名、問題...等都當成聊天    指令格式:   chat()
    範例:
    你是誰？        chat()
    你會什麼？      chat()
    今天幾號？      chat()
    你喜歡什麼？    chat()
    誰比較厲害？    chat()
    牛頓            chat()
    愛因斯坦        chat()
    量子力學        chat()

Note:
1. 返回 格式字串，不要添加任何額外的文字或說明。
2. 只使用 forward backward resume pause next play close query chat 當指令，
    千萬不要自作聰明，不要自創指令。
3. 指令格式為 指令(關鍵字)，指令一定加()
4. 關鍵字不要翻成英文，直接用原來的關鍵字。
"""

prompt_main_1 = """
你是一個指令分析器，根據你收到的訊息，轉換成
forward backward resume pause next play close query chat 的指令，
轉換規則，指令格式如下：

1. 訊息: 快轉       指令格式:  forward 時間轉成秒數，沒有時間則設成10
    範例:
    快轉            forward 10
    快轉 時間       forward 時間轉成秒數

2. 訊息: 倒轉       指令格式:   backward 時間轉成秒數，沒有時間則設成10
    範例:
    倒轉            backward 10 
    倒轉 時間       backward 時間轉成秒數 

3. 訊息: 繼續       指令格式: resume
4. 訊息: 暫停       指令格式: pause
5. 訊息: 下一個     指令格式: next

6. 訊息: 搜尋 關鍵字    指令格式:   play 關鍵字
   訊息: 搜尋           指令格式:   query 請問要搜尋什麼
    範例:
    搜尋抒情歌      play 抒情歌
    搜尋            query 請問要搜尋什麼

7. 敘述: 聽\撥歌\撥放 關鍵字   指令格式:    play 關鍵字
   敘述: 聽\撥歌\撥放         指令格式:     query 請問要撥的歌
    範例:
    聽伍佰的歌      play 伍佰的歌
    聽              query 請問要聽什麼

8. 訊息: 看\我想看 關鍵字     指令格式:     play 關鍵字
   訊息: 看\我想看            指令格式:     query 請問要看什麼
   範例:
    我想看新聞      play 新聞
    我想看          query 請問要看什麼

9. 訊息: 關閉               指令格式:   close

10. 其他無法識別的指令，天氣、人名、問題...等都當成聊天    指令格式:   chat
    範例:
    你是誰？        chat
    你會什麼？      chat
    今天幾號？      chat
    你喜歡什麼？    chat
    誰比較厲害？    chat
    牛頓            chat
    愛因斯坦        chat
    量子力學        chat

Note:
1. 返回 格式字串，不要添加任何額外的文字或說明。
2. 只使用 forward backward resume pause next play close query chat 當指令，
    千萬不要自作聰明，不要自創指令。
3. 關鍵字不要翻成英文，直接用原來的關鍵字。
"""

prompt_query = f"""
你詢問使用者，根據使用者的回答，轉成以下的指令格式字串：
使用者的回答: 取消               指令格式:    cancel()
使用者的回答: 取消之外的回答      指令格式:     play(使用者的回答)
範例:
取消                cancel()
忘情水              play(忘情水)
今夜你會不會來      play(今夜你會不會來)

Note:
1. 返回 格式字串，不要添加任何額外的文字或說明。
2. 只使用 cancel play 當指令，千萬不要自作聰明，不要自創指令。
3. 指令格式為 指令(關鍵字)，指令一定加()
4. 關鍵字不要翻成英文，直接用原來的關鍵字。
"""

def process_command_debug(command, user_input):
    [cmd,args] = parse_command(command)
    if cmd == "ask":
        print("Chatbot:")
        if len(args) > 0:
            print(args[0])
        user_input = get_user_input()
        assistant_ask(user_input)
    
def assistant_query(user_input):
    response = ollama.chat(model=LLM_MODEL_NAME, messages=[
        {"role": "system", "content": prompt_query},
        {"role": "user", "content": user_input},
    ], stream=False)
    command = response["message"]["content"]
    if DEBUG: print('cmd:',command)
    process_command(command, user_input)

def assistant_main(user_input):
    response = ollama.chat(model=LLM_MODEL_NAME, messages=[
        {"role": "system", "content": prompt_main_1},
        {"role": "user", "content": user_input},
    ], stream=False)
    command = response["message"]["content"]
    if DEBUG: print('cmd:',command)
    process_command(command, user_input)

def assistant_chat(user_input):
    # prompt = f"""
    # 你是一個性感風騷的女僕，請用挑逗的語氣回答問題。
    # """
    prompt = f"""
    你是一個智能語音助手，請用輕鬆的語氣回答問題。
    """
    response = ollama.chat(model=LLM_MODEL_NAME, messages=[
        {"role": "system", "content": prompt},
        {"role": "user", "content": user_input},
    ], stream=True)

    process_stream(response)

def assistant_init():
    prompt = f"""
    你剛剛啟動了，請用繁體中文回答問題。
    """
    response = ollama.chat(model=LLM_MODEL_NAME, messages=[
        {"role": "system", "content": prompt},
        {"role": "user", "content": ""},
        {"role": "assistant", "content": "歡迎使用！"},
    ], stream=True)
    
    #print("Chatbot: ", response['message']['content'])
    process_stream(response)

def assistant_read():
    response = ollama.chat(model=LLM_MODEL_NAME, messages=[
        {"role": "user", "content": news+'\n\n念出新聞內容'},
    ], stream=True)
    
    #print("Chatbot: ", response['message']['content'])
    process_stream(response)

def process_stream(stream):
    print("Chatbot: ")
    full_response = ""
    for chunk in stream:
        print(chunk['message']["content"], end='', flush=True)
        if SPEECH is True:
            # Collect the response in chunks
            full_response += chunk['message']["content"]
            if "\n" in full_response or any(p in full_response for p in "，。！？；："):
                text_to_speech(full_response)
                full_response = ""
    if full_response:
        if SPEECH is True: text_to_speech(full_response)
    print('\n')


def cmd_youtube(cmd, args):
    ret = cmd_yt.execute(cmd, args)
    msg(ret['text'])

def execute_command_query(args):
    print("Chatbot:")
    if len(args) > 0: msg(args[0])
    else: msg("請說")
    print("你:")
    user_input = get_user_input()
    assistant_query(user_input)

def process_command(command, user_input):
    [cmd, args] = parse_command_1(command)
    match cmd:
        case "chat":
            assistant_chat(user_input)
        case "query":
            execute_command_query(args)
        case "cancel":
            print("Chatbot:")
            msg("取消")
        case "pause" | "resume" | "next" | "close" | "forward" | "backward" | "play":
            cmd_youtube(cmd, args)
        case _:
            # msg("無法識別的指令")
            assistant_chat(user_input)

def parse_command(text):
    # 使用正則表達式擷取命令名稱與參數
    match = re.match(r'\s*(\w+)\s*\(\s*(.*)\s*\)\s*', text)
    if match:
        cmd = match.group(1)  # 取得命令名稱（play）
        args_str = match.group(2).strip()  # 取得括號內的參數（去掉前後空格）
        # 如果參數非空，則以逗號分隔並去除空格，否則回傳空列表
        args = [arg.strip() for arg in args_str.split(',')] if args_str else []
        ret = [cmd, args]
    else:
        ret = [text, []]
    
    if DEBUG: print('parse:',ret)
    return ret


def parse_command_1(text):
    sps = text.strip().replace('(',' ').replace(')',' ').split()
    print(sps, len(sps))
    if len(sps) > 0: cmd = sps[0]; args = sps[1:]
    else: cmd=''; args=[]
    ret = [cmd, args]
    if DEBUG: print('parse:',ret)
    return [cmd, args]              
    
def get_user_input():
    if SPEAK:
        while True:
            user_input = sr.recognition() 
            if user_input is None: continue
            return user_input
    else: return input()

def msg(message):
    print(message)
    if SPEECH is True:
        text_to_speech(message)
    
    
DEBUG = True
SPEAK = False
SPEECH = True

def chat():

    # assistant_read()
    # assistant_start()
    #print("Chatbot: 你好！")
    # init()

    while True:
        print("你:")
        user_input = get_user_input()

        if user_input is None:
            continue  # 如果辨識失敗，則繼續循環

        if user_input.lower() in ["exit", "quit", "離開"]:
            print("Chatbot:")
            msg("再見！")
            break

        #process_command(user_input)
        #assistant_parser(user_input)
        #assistant_noraml(user_input)
        assistant_main(user_input)


if __name__ == "__main__":
    chat()