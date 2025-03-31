import gtts
import io
import pygame

#功能說明 : 將 text 轉成語音並播放

def text_to_speech(text):
    text = text.replace('*', '').strip()
    if text == '': return  # If the text is empty after cleaning, do nothing
    tts = gtts.gTTS(text, lang='zh-tw')
    tts_fp = io.BytesIO()
    tts.write_to_fp(tts_fp)
    tts_fp.seek(0) # Reset the file pointer to the beginning

    pygame.mixer.init()
    pygame.mixer.music.load(tts_fp, 'mp3')
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)  # Wait for the sound to finish playing    

# 單元測試
# 功能說明 : 測試 text_to_speech 函數是否正常運作
# 測試內容 : 將測試語音轉成 mp3 檔案並播放
def unit_test():
    text = "這是一個測試語音的範例。"
    text_to_speech(text)

# 測試用的語音
if __name__ == "__main__":
    unit_test()