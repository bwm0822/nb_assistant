import requests
from bs4 import BeautifulSoup

headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

global contents, index
contents = []
index = 0

# 這個模組用於從 DuckDuckGo 搜尋，並提取搜尋結果的網址和標題
def get_search_results(query):
    if query == '': return {"status":-1, "msg":"搜尋關鍵字為空"}

    # 使用 DuckDuckGo 搜尋
    search_url = f"https://duckduckgo.com/html/?q={query}"
    

    response = requests.get(search_url, headers=headers)

    # 嘗試手動設定編碼
    response.encoding = response.apparent_encoding  # 自動偵測編碼
    # print(f"偵測到的編碼: {response.encoding}")  # 印出偵測到的編碼

    soup = BeautifulSoup(response.text, "html.parser")
    
    # 解析搜尋結果
    global contents, index
    contents = []
    index = 0
    for link in soup.find_all("a", class_="result__a"):
        contents.append((link["href"], link.text))

    if len(contents) == 0:
        return {"status":-1, "msg":"沒有搜尋結果"}
    

    return {"status":1, "content":contents}  # 回傳搜尋結果


# 這個模組用於從指定的網址提取網頁內容
def get_page_content(url):
    print(f"正在提取網址: {url}")
    try:
        response = requests.get(url, headers=headers)
        response.encoding = response.apparent_encoding  # 自動偵測編碼
        soup = BeautifulSoup(response.text, "html.parser")
        # 提取所有文字內容
        # text_content = soup.get_text(separator="\n", strip=True)

        content_div = soup.find("div")
        text_content = content_div.get_text(separator="\n", strip=True)

        return {"status":1, "content":text_content}

    except requests.exceptions.SSLError:
        return {"status":-1, "msg":"SSL 驗證失敗，請檢查網址或稍後再試。"}
    
def search(query):
    result = get_search_results(query)
    if result["status"] == -1:
        return result
    url, title = contents[1]
    return get_page_content(url)

def next():
    global index
    index += 1
    if index >= len(contents):
        return {"status": -1, "msg": "沒有更多搜尋結果"}
    url, title = contents[index]
    return get_page_content(url)    

    
    
def execute(cmd, args):
    arg = args[0] if len(args)>0 else ''
    match cmd:
        case "search":
            return search(arg)
        case 'page':
            return next()
        case _:
            return {"status": -1, "msg": "無效的指令"}



# 單元測試
# 功能說明 : 測試 get_search_results 和 get_page_content 函數是否正常運作
# 測試內容 : 將測試關鍵字轉成搜尋結果並顯示網頁內容
def unit_test():
    query = input("請輸入你想搜尋的關鍵字:")
    result = get_search_results(query)
    
    if result["status"] == -1:
        print(result['msg'])
        return

    for url, title in result['content']:
        print(f"標題: {title}")
        print(f"網址: {url}")
        print("-" * 80)
        user_input = input("按 Enter 鍵查看網頁內容, n 略過, q 離開")  # 等待用戶輸入以查看網頁內容
        if user_input.lower() == "q":
            break
        elif user_input.lower() == "n":
            continue
    
        result = get_page_content(url)
        if result["status"] == -1:
            print(result['msg'])
        else:
            print("網頁內容:")
            print(result['content'])
            print("=" * 80)

        user_input = input("按 Enter 鍵繼續, q 離開")  # 等待用戶輸入以查看下一個結果
        if user_input.lower() == "q":
            break

# 測試用的搜尋
if __name__ == "__main__":
    unit_test()