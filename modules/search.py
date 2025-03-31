import requests
from bs4 import BeautifulSoup

headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

# 這個模組用於從 DuckDuckGo 搜尋，並提取搜尋結果的網址和標題
def get_search_results(query):
    # 使用 DuckDuckGo 搜尋
    search_url = f"https://duckduckgo.com/html/?q={query}"
    
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 解析搜尋結果
    results = []
    for link in soup.find_all("a", class_="result__a"):
        results.append((link["href"], link.text))
    
    return results


# 這個模組用於從指定的網址提取網頁內容
def get_page_content(url):
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        # 提取所有文字內容
        text_content = soup.get_text(separator="\n", strip=True)
        return text_content

    except requests.exceptions.SSLError:
        print("SSL 驗證失敗，請檢查網址或稍後再試。")
        return None



# 單元測試
# 功能說明 : 測試 get_search_results 和 get_page_content 函數是否正常運作
# 測試內容 : 將測試關鍵字轉成搜尋結果並顯示網頁內容
def unit_test():
    query = "新聞頭版"  # 替換為你想搜尋的關鍵字
    results = get_search_results(query)
    
    for url, title in results:
        print(f"標題: {title}")
        print(f"網址: {url}")
        print("-" * 80)
        user_input = input("按 Enter 鍵查看網頁內容, n 略過, q 離開")  # 等待用戶輸入以查看網頁內容
        if user_input.lower() == "q":
            break
        elif user_input.lower() == "n":
            continue

        content = get_page_content(url)
        print("網頁內容:")
        print(content)
        print("=" * 80)

        user_input = input("按 Enter 鍵繼續, q 離開")  # 等待用戶輸入以查看下一個結果
        if user_input.lower() == "q":
            break

# 測試用的搜尋
if __name__ == "__main__":
    unit_test()