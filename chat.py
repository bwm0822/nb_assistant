import ollama
import re
import modules.cmd_selenium_yt as cmd_yt
import modules.recognise as sr
from modules.speech import text_to_speech
import json

LLM_MODEL_NAME = "llama3.2"

global driver
driver = None

def parse_command(user_input):
    prompt = f"""
    你是一個 Python 開發者，
    請根據要求生成一段 Python 程式碼來控制電腦，
    請返回可以執行的 Python 程式碼，代碼需要能夠正確執行並控制電腦。
    不要添加任何額外的文字或說明。
    """
    response = ollama.chat(model=LLM_MODEL_NAME, messages=[
        {"role": "system", "content": prompt},
        {"role": "user", "content": user_input},
        ])
    return response

    # 我想聽          {{"command": "search", "args": ["關鍵字"]}}

def assistant_start():
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

#沒有關鍵字時，詢問使用者要搜尋的關鍵字。使用 "ask" "{{\"command\": \"ask\", \"args\": [\"詢問關鍵字\"]}}"
def assistant_parser(user_input):
    prompt = f"""
    你是一個指令分析器，你接收以下的指令，並轉化為格式的 JSON 字串：
    開啟 YouTube            "{{\"command\": \"open\", \"args\": []}}"
    關閉 YouTube            "{{\"command\": \"close\", \"args\": []}}"
    繼續                    "{{\"command\": \"resume\", \"args\": []}}"
    暫停                    "{{\"command\": \"pause\", \"args\": []}}"
    播放下一部              "{{\"command\": \"next\", \"args\": []}}"
    快轉                    "{{\"command\": \"forward\", \"args\": [\"時間轉成秒數\"]}}"
    倒轉                    "{{\"command\": \"backward\", \"args\": [\"時間轉成秒數\"]}}"

    當指令為 搜尋/聽歌/撥放 時，有取得歌名時，使用 "play" "{{\"command\": \"play\", \"args\": [\"歌名\"]}}"
    
          
    

    狀態                    "{{\"command\": \"status\", \"args\": []}}"          
    對於 聊天/無法識別的指令 會用另一個對話來處理，所以不用回覆，直接輸出  "{{\"command\": \"chat\", \"args\": []}}"
    
    NOTE : 
        1. 返回 JSON 格式的字串，不要添加任何額外的文字或說明。
        2. 只輸出我有列出來ˊ的 command。
        3. 輸出會被解析成 JSON 格式，所以要注意格式的正確性。   
    """
    response = ollama.chat(model=LLM_MODEL_NAME, messages=[
        {"role": "system", "content": prompt},
        {"role": "user", "content": user_input},
    ], stream=False)

    json_response = toJSON(response)
    if json_response is not None:
        process_command(json_response, user_input)
    else:
        print("無法解析指令，請重新輸入。")

# unknown("無法識別的指令")

def assistant_main(user_input):
    prompt = f"""
    你是一個指令分析器，你接收以下的指令，並轉化以下格式字串：
    快轉    指令 forward(將時間轉成秒數，如果沒有時間就設成10)
    倒轉    指令 backward(將時間轉成秒數，如果沒有時間就設成10)
    繼續    指令 resume()
    暫停    指令 pause()
    下一個  指令 next()
    搜尋        指令 play(關鍵字)，一般是歌名或關鍵字，如果沒有關鍵字就詢問使用者要搜尋的關鍵字。
    撥歌\聽歌   指令 play(關鍵字)，一般是歌名或關鍵字，如果沒有關鍵字就詢問使用者要搜尋的關鍵字。
    看\我想看   指令 play(關鍵字)，一般是歌名或關鍵字，如果沒有關鍵字就詢問使用者要搜尋的關鍵字。
    關閉    指令 close()
    
    NOTE : 
        1. 返回 格式字串，不要添加任何額外的文字或說明。
        2. 只輸出上面有列的指令，不要自創指令。
        3. 指令格式為 指令(關鍵字)，指令一定加()
        3. 無法判斷的指令則輸出 chat()
        4. 關鍵字不要翻成英文，直接用原來的關鍵字。
    """
    response = ollama.chat(model=LLM_MODEL_NAME, messages=[
        {"role": "system", "content": prompt},
        {"role": "user", "content": user_input},
    ], stream=False)

    print(response["message"]["content"])
    process_command(response["message"]["content"], user_input)
    # json_response = toJSON(response)
    # if json_response is not None:
    #     process_command(json_response, user_input)
    # else:
    #     print("無法解析指令，請重新輸入。")

def assistant_chat(user_input):
    prompt = f"""
    你是一個性感風騷的女僕，請用挑逗的語氣回答問題。
    """
    response = ollama.chat(model=LLM_MODEL_NAME, messages=[
        {"role": "system", "content": prompt},
        {"role": "user", "content": user_input},
    ], stream=True)

    process_stream(response)

def assistant_noraml(user_input): 
    prompt = f"""
    你是一個智能語音助手，請用輕鬆的語氣回答問題。
    """
    response = ollama.chat(model=LLM_MODEL_NAME, messages=[
        {"role": "system", "content": prompt},
        {"role": "user", "content": user_input},
    ], stream=True)

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

# 執行生成的 Python 程式碼
def execute_generated_code(generated_code):
    print(generated_code)
    try:
        # 將生成的程式碼執行
        exec(generated_code)
        return "程式執行成功！"
    except Exception as e:
        return f"程式執行錯誤: {str(e)}"

def execute_command_youtube(command, args):
    global driver  # Declare driver as global to modify the global variable
    match command:
        case "pause":
            if driver is not None: cmd_yt.pause(driver)
        case "resume":
            if driver is not None: cmd_yt.resume(driver)
        case "next":
            if driver is not None: cmd_yt.next(driver)
        case "open":
            if driver is None: driver = cmd_yt.open()
        case "close":
            if driver is not None: driver = cmd_yt.close(driver)
        case "forward":
            if driver is not None: cmd_yt.forward(driver, args)
        case "backward":
            if driver is not None: cmd_yt.backward(driver, args)
        case "play":
            if driver is None: driver = cmd_yt.open()
            cmd_yt.search_and_play(driver, args)
        case "status":
            cmd_yt.get_status(driver)

def execute_command_ask(command, args):
    print("Chatbot: ", args[0])
    text_to_speech(args[0])

def process_command_json(json, user_input):
    cmd = json["command"]
    if cmd == "chat": assistant_chat(user_input)
    elif cmd == "ask": execute_command_ask(cmd, json["args"])
    else: execute_command_youtube(cmd, json["args"])

def process_command(command, user_input):
    [cmd,args] = parse_command(command)
    print(command,'->',cmd,args)
    # if cmd == "chat": assistant_chat(user_input)
    # else: execute_command_youtube(cmd, args)
    execute_command_youtube(cmd, args)

def parse_command(text):
    # 使用正則表達式擷取命令名稱與參數
    match = re.match(r'\s*(\w+)\s*\(\s*(.*)\s*\)\s*', text)
    if match:
        cmd = match.group(1)  # 取得命令名稱（play）
        args_str = match.group(2).strip()  # 取得括號內的參數（去掉前後空格）

        # 如果參數非空，則以逗號分隔並去除空格，否則回傳空列表
        args = [arg.strip() for arg in args_str.split(',')] if args_str else []

        return [cmd, args]
    else:
        return [text, []]

def toJSON(response):
    try:
        response = response['message']['content'].strip().replace('}"', '}')
        json_response = json.loads(response)
        print(response, ' -> ' ,json_response)
        return json_response
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None

# def speech_recognition(r):
    with sr.Microphone() as source:
        print("你: ")
        r.adjust_for_ambient_noise(source, duration=1)  # 適應環境噪音
        audio = r.listen(source)

        try:
            command = r.recognize_google(audio, language="zh-TW")  # 語言設定為繁體中文
            print("語音辨識:",command)
            return command
        except sr.UnknownValueError:
            print("無法辨識語音，請再試一次。")
            return None
        except sr.RequestError:
            print("無法連線到 Google 語音服務，請檢查網路。")
            return None

        command = r.recognize_google(audio, language="zh-TW")
        print(command)
        return command
    
def get_user_input():
    if SPEAK: return sr.recognition()
    else: return input("You: ")

SPEAK = True
SPEECH = True

def chat():

    # assistant_start()
    #print("Chatbot: 你好！")

    while True:
        print("你:")
        user_input = get_user_input()

        if user_input is None:
            continue  # 如果辨識失敗，則繼續循環

        if user_input.lower() in ["exit", "quit", "離開"]:
            print("Chatbot: 再見！")
            break

        #process_command(user_input)
        #assistant_parser(user_input)
        #assistant_noraml(user_input)
        assistant_main(user_input)


if __name__ == "__main__":
    chat()