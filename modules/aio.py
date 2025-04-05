
import asyncio
import threading
import time

def task1():
    print("Task 1 開始")
    time.sleep(3)
    print("Task 1 完成")

def task2():
    print("Task 2 開始")
    time.sleep(10)
    print("Task 2 完成")

def new_task(task):
    threading.Thread(target=task, daemon=True).start()  # 在新執行緒執行



while True:
    user_input = input("請按 Enter 鍵開始:")
    match user_input:
        case 'q':
            print("退出")
            break
        case '1':
            new_task(task1)
        case '2':
            new_task(task2)
        case _:
            print("無效的輸入")






