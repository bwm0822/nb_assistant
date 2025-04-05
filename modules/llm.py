import ollama
import threading
if __name__ == "__main__":
    from speech import text_to_speech
else:
    from modules.speech import text_to_speech

LLM_MODEL_NAME = "llama3.2"

DEBUG = True
SPEAK = False
SPEECH = True

global current_thread
current_thread = None

pause_event = threading.Event()
stop_event = threading.Event()

prompt_main_1 = """
你是一個指令分析器，根據你收到的訊息，轉換成
forward backward resume pause next play close query chat search 的指令，
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

10. 搜尋 關鍵字         指令格式:   search 關鍵字
    範例:
    搜尋頭條新聞        search 頭條新聞

11. page            指令格式:   page
    範例:
        page        指令格式:   page

11. 其他無法識別的指令，天氣、人名、問題...等都當成聊天    指令格式:   chat
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
2. 只使用 forward backward resume pause next play close query chat search 當指令，
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

def thread(target, user_input):
    global current_thread
    if current_thread is not None:
        stop_event.set()    # 停止執行緒
        pause_event.set()  # 防止還在等待
        print("---- wait ----")
        current_thread.join()
        print("---- done ----")

    pause_event.set()  # 預設為不暫停狀態
    stop_event.clear()  # 預設為不停止狀態
    # Create a thread to run the assistant_chat function
    current_thread = threading.Thread(target=target, args=(user_input,))
    current_thread.start()
    # Wait for the thread to finish
    # chat_thread.join()
    return {"status": 1, "msg": "執行緒啟動成功"}


def assistant_main(user_input):
    response = ollama.chat(model=LLM_MODEL_NAME, messages=[
        {"role": "system", "content": prompt_main_1},
        {"role": "user", "content": user_input},
    ], stream=False)
    return response["message"]["content"]

def assistant_query(user_input):
    response = ollama.chat(model=LLM_MODEL_NAME, messages=[
        {"role": "system", "content": prompt_query},
        {"role": "user", "content": user_input},
    ], stream=False)
    return response["message"]["content"]
    # process_command(command, user_input)

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
    global current_thread
    current_thread = None  # 重置執行緒變數
    print("---- 執行緒結束 ----")


def process_stream(stream):
    print("Chatbot: ")
    full_response = ""
    for chunk in stream:

        if pause_event.is_set() is False:
            print("⏸ 暫停輸出")
            pause_event.wait()

        if stop_event.is_set():
            print("🛑 停止執行緒")
            return
        
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

def execute(cmd, args):
    arg = args[0] if len(args) > 0 else ''
    match cmd:
        case "main":
            return assistant_main(arg)
        case "query":
            return assistant_query(arg)
        case "chat":
            return thread(assistant_chat, arg)
        case "pause":
            pause_event.clear()
            return {"status": 1, "msg": "暫停LLM"}
        case "resume":
            pause_event.set()
            return {"status": 1, "msg": "繼續LLM"}
        case "stop":
            stop_event.set()    # 停止執行緒
            pause_event.set()  # 防止還在等待
            return {"status": 1, "msg": "停止執行緒"}
        case _:
            return {"status": -1, "msg": "無效的指令"}



def unit_test():
    while True:
        user_input = input("請輸入你想詢問的問題，按 q 離開\n")
        if user_input.lower() == "q": break
        sps = user_input.strip().split()
        print(sps, len(sps))
        if len(sps) > 0: cmd = sps[0]; args = sps[1:]
        else: cmd=''; args=[]
        print(f"指令: {cmd}, 參數: {args}")
        print(execute(cmd, args))


if __name__ == "__main__":
    unit_test()