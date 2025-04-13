import ollama
import threading
import time
if __name__ == "__main__":
    import cmd_mpv as youtube
    # import cmd_vlc as youtube
    from speech import text_to_speech
    import prompts
else:
    import modules.cmd_mpv as youtube
    # import modules.cmd_vlc as youtube
    from modules.speech import text_to_speech
    import modules.prompts as prompts


LLM_MODEL_NAME = "llama3.2"
# LLM_MODEL_NAME = "mistral"

SPEECH = True
DEBUG = False
global current_thread, is_pause, _user_input
current_thread = None
is_pause = False
_user_input = ''
pause_event = threading.Event()
stop_event = threading.Event()

def tools(): 
    return [
        {
            "type": "function",
            "function": {
                "name": "tool_chat",
                "description": "",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "使用者的輸入內容"
                        }
                    },
                    "required": ['content']
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "tool_stop_chat",
                "description": "stop the chat",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "tool_end",
                "description": "end the application",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "tool_get_time",
                "description": "",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
         {
            "type": "function",
            "function": {
                "name": "tool_get_date",
                "description": "",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    ]


def debug(*args):
    if DEBUG: print(args)

def pause():
    global is_pause
    is_pause = youtube.is_pause()
    youtube.execute("pause")
    pause_event.clear()  # 設定為暫停狀態
    debug("---- 暫停 ----")

def resume():
    if not is_pause: youtube.execute("resume")
    pause_event.set()  # 清除暫停狀態
    debug("---- 繼續 ----")

def stop():
    stop_event.set()    # 停止執行緒
    pause_event.set()  # 防止還在等待
    debug("---- 停止 ----")

def clear():
    # 清除暫停狀態和停止狀態
    stop_event.clear()
    pause_event.set()
    debug("---- 清除 ----")

def get_time():
    # return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    return time.strftime("%H:%M", time.localtime())

def get_date():
    return time.strftime("%Y-%m-%d", time.localtime())

def msg(message):
    print(message)
    if SPEECH is True: text_to_speech(message)

def thread(target, user_input):
    global current_thread
    if current_thread is not None:
        stop()
        debug("---- wait ----")
        current_thread.join()
        debug("---- done ----")

    clear()
    # Create a thread to run the assistant_chat function
    current_thread = threading.Thread(target=target, args=(user_input,))
    current_thread.start()
    # Wait for the thread to finish
    # chat_thread.join()
    return {"status": 1, "msg": "執行緒啟動成功", "type": "thread"}    

def chat(user_input):
    # prompt = f"""
    # 你是一個性感風騷的女僕，請用挑逗的語氣回答問題。
    # """
    prompt = f"""
    你是一個智慧語音助理，請用輕鬆的語氣回答問題。
    """
    response = ollama.chat(model=LLM_MODEL_NAME, messages=[
        {"role": "system", "content": prompt},
        {"role": "user", "content": "不要轉換文字格式，例如: '黃大偉的歌' 不要轉成 \u738b\u516c\u4e2d\u7a76\u4e3f"},
        {"role": "user", "content": "我叫Rex"},
        {"role": "user", "content": user_input},
    ], stream=True)

    process_stream(response)
    debug("---- 執行緒結束 ----")


def process_stream(stream):
    print("AI: ")
    full_response = ""
    for chunk in stream:

        if pause_event.is_set() is False:
            debug("⏸ 暫停執行緒")
            pause_event.wait()

        if stop_event.is_set():
            debug("🛑 停止執行緒")
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


def main(user_input):
    global _user_input
    _user_input = user_input
    messages = [
        {"role": "system", "content": prompts.system_prompt},
        {"role": "user", "content": user_input}]

    response = ollama.chat(
        model = LLM_MODEL_NAME,
        messages = messages,
        tools = tools()+youtube.tools())

    # print("response: ", response)

    if 'tool_calls' in response['message']:
        for tool_call in response['message']['tool_calls']:
            ret = process_toolcall(tool_call)
            if 'status' in ret: return ret
            tool_response = {"role": "tool", "content": ret}
            messages.append(response['message'])
            messages.append(tool_response)
            debug("messages: ", messages)

        full_response = ollama.chat(
            model=LLM_MODEL_NAME,
            messages=messages)

        print('AI:')
        return {'status':1, 'msg':full_response.message.content}

    else:
        print('AI:')
        return {'status':1, 'msg':response.message.content}
    


def process_toolcall(tool_call):
    debug("🎯 Tool call received:", tool_call)
    debug("🎯 Tool call received:", tool_call.function.name)
    arguments = tool_call.function.arguments
    name = tool_call.function.name 
    if name in functions: return functions[name](arguments)
    else: return {'status': 0, 'msg': f'未知的工具呼叫: {name}'}


def tool_play(arguments):    
    title = arguments.get('title','')
    # print("title: ", title)
    msg(f"搜尋:{title}，請稍後...")
    return youtube.execute('play', title)

def tool_volumeup(arguments):
    return youtube.execute('volumeup')

def tool_volumedn(arguments):
    return youtube.execute('volumedn')

def tool_volume(arguments):
    volume = arguments.get('volume',50)
    return youtube.execute('volume', volume)

def tool_mute(arguments):
    on = arguments.get('on',True)
    return youtube.execute('mute', on)

def tool_forward(arguments):
    seconds = arguments.get('seconds',10)
    return youtube.execute('forward', seconds)

def tool_backward(arguments):
    seconds = arguments.get('seconds',10)
    return youtube.execute('backward', seconds)

def tool_pause(arguments):
    global is_pause
    is_pause = True
    return youtube.execute('pause')

def tool_resume(arguments):
    return youtube.execute('resume')

def tool_close(arguments):
    return youtube.execute('close')

def tool_next(arguments):
    return youtube.execute('next')

def tool_previous(arguments):
    return youtube.execute('previous')

def tool_end(arguments):
    stop()
    print("AI:")
    msg("再見！主人")
    return {'status': 1, 'msg': '結束', 'type': 'end'}

def tool_chat(arguments):
    youtube.execute('pause')
    # content = arguments.get('content','')
    return thread(chat, _user_input)

def tool_stop_chat(arguments):
    stop()
    return {'status': 1, 'msg': '取消聊天'}

def tool_get_volume(arguments):
    return youtube.execute('get_volume').get('msg', '')

def tool_get_time(arguments):
    return get_time()

def tool_get_date(arguments):
    return get_date()
    

    
functions = {
    'tool_play': tool_play,
    'tool_volumeup': tool_volumeup,
    'tool_volumedn': tool_volumedn,
    'tool_volume': tool_volume,
    'tool_mute': tool_mute,
    'tool_forward': tool_forward,
    'tool_backward': tool_backward,
    'tool_pause': tool_pause,
    'tool_resume': tool_resume,
    'tool_close': tool_close,
    'tool_next': tool_next,
    'tool_previous': tool_previous,
    'tool_chat': tool_chat,
    'tool_stop_chat': tool_stop_chat,
    'tool_end': tool_end,
    'tool_get_volume': tool_get_volume,
    'tool_get_time': tool_get_time,
    'tool_get_date': tool_get_date
}


def unit_test():
    while True:
        user_input = input("請輸入問題：")
        if user_input.lower() == 'exit':
            break
        elif user_input.lower() == 'clear':
            print("\033[H\033[J", end='')
        else:
            main(user_input)


if __name__ == "__main__":
    unit_test()
    # print(get_date())
    # print(get_time())
   
   


# debug("🎯 Tool call received:", tool_call)
            # debug("🎯 Tool call received:", tool_call.function.name)
            # arguments = tool_call.function.arguments
            # fname = tool_call.function.name 

            # match fname:
            #     case 'play':
            #         title = arguments.get('title','')
            #         # print("title: ", title)
            #         msg(f"搜尋:{title}，請稍後...")
            #         return youtube.execute(fname, title)
            #     case 'volumeup'|'volumedn':
            #         return youtube.execute(fname)
            #     case 'volume':
            #         volume = arguments.get('volume',50)
            #         return youtube.execute(fname, volume)
            #     case 'mute':
            #         on = arguments.get('on',True)
            #         return youtube.execute(fname, on)
            #     case 'forward'|'backward':
            #         seconds = arguments.get('seconds',10)
            #         return youtube.execute(fname, seconds)
            #     case 'pause':
            #         global is_pause
            #         is_pause = True
            #         return youtube.execute(fname)
            #     case 'resume'|'close'|'next'|'previous':
            #         return youtube.execute(fname)
            #     case 'chat':
            #         youtube.execute('pause')
            #         return thread(chat,user_input)
            #     case 'stop_chat':
            #         stop()
            #         return {'status': 1, 'msg': '取消聊天'}
            #     case 'end':
            #         stop()
            #         print("AI:")
            #         msg("再見！主人")
            #         return {'status': 1, 'msg': '結束', 'type': 'end'}
            #     case 'get_volume':
            #         tool_response = {
            #                 "role": "tool",
            #                 "content": f"{youtube.execute(fname).get('msg', '')}"
            #             }
            #     case 'get_time':
            #         tool_response = {
            #                 "role": "tool",
            #                 "content": f"{get_time()}"
            #             }
            #     case 'get_date':
            #         tool_response = {
            #                 "role": "tool",
            #                 "content": f"{get_date()}"
            #             }
            #     case _:
            #         tool_response = {
            #             "role": "tool",
            #             "content": f"未知的工具呼叫"
            #         }

            # messages=messages+[response['message'],tool_response]