import ollama
import re
# import modules.cmd_selenium_yt as cmd_yt
import modules.cmd_yt_dlp_list as cmd_yt
import modules.search as page
import modules.recognise as sr
# import modules.recognise_webrtc as sr
from modules.speech import text_to_speech
import json
import modules.llm as llm


def cmd_youtube(cmd, args):
    ret = cmd_yt.execute(cmd, args)
    msg(ret['msg'])

def cmd_page(cmd, args):
    ret = page.execute(cmd, args)
    if ret['status'] == -1:
        msg(ret['msg'])
    else:
        content=f"內容:{ret['content']},從內容擷取:{args[0]}"
        print(content)
        # assistant_read(content)

def query(args):
    print("Chatbot:")
    if len(args) > 0: msg(args[0])
    else: msg("請說")
    print("你:")
    user_input = get_user_input()
    # assistant_query(user_input)
    command = llm.execute("query", [user_input])
    process_command(command, user_input)

def process_command(command, user_input):
    [cmd, args] = parse_command_1(command)
    match cmd:
        case "chat":
            # thread_assistant_chat(user_input)
            llm.execute("chat", [user_input])
        case "query":
            query(args)
        case "cancel":
            print("Chatbot:")
            msg("取消")
        case "pause" | "resume" | "next" | "close" | "forward" | "backward" | "play":
            cmd_youtube(cmd, args) 
        case "search" | "page":
            cmd_page(cmd, args)
        case _:
            msg("無法識別的指令")
            # thread_assistant_chat(user_input)
            llm.execute("chat", [user_input])

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
    
def wakeup():
    print("sleeping...")
    while True:
        user_input = sr.recognition() 
        if user_input == '夥計': 
            msg("是的，老哥")
            return

def get_user_input():
    if SPEAK:
        while True:
            user_input = sr.recognition(10) 
            # if user_input is None: continue
            return user_input
    else: return input()

def msg(message):
    print(message)
    if SPEECH is True:
        text_to_speech(message)
    
def topic(user_input):
    command = llm.execute("main", [user_input])
    process_command(command, user_input)

DEBUG = True
SPEAK = True
SPEECH = True
HOTWORD = True

def chat():

    # assistant_read()
    # assistant_start()
    #print("Chatbot: 你好！")
    # init()

    while True:
        # wakeup()
        print("你:")
        user_input = get_user_input()
        if user_input is None: continue

        if user_input.lower() in ["exit", "quit", "離開"]:
            print("Chatbot:")
            msg("再見！")
            break

        #process_command(user_input)
        #assistant_parser(user_input)
        #assistant_noraml(user_input)
        # assistant_main(user_input)
        topic(user_input)


if __name__ == "__main__":
    chat()