import gtts
import io
import pygame

#功能說明 : 將 text 轉成語音並播放
def text_to_speech(text):
    strip = text.replace('*', '').strip()
    if not strip: print("Error: No text to convert to speech."); return
    try:
        tts = gtts.gTTS(strip, lang='zh-tw')
        tts_fp = io.BytesIO()
        tts.write_to_fp(tts_fp)
        tts_fp.seek(0) # Reset the file pointer to the beginning

        pygame.mixer.init()
        pygame.mixer.music.load(tts_fp, 'mp3')
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)  # Wait for the sound to finish playing   
    except Exception as e:
        print("text_to_speech:", text)
        print("Exception:", e)

# 單元測試
# 功能說明 : 測試 text_to_speech 函數是否正常運作
# 測試內容 : 將測試語音轉成 mp3 檔案並播放
def unit_test():
    while True:
        text = input("請輸入文字：")
        if text.lower() == 'exit':
            break
        elif text.lower() == 'clear':
            print("\033[H\033[J", end='')
        else:
            text_to_speech(text)

def test():
    # text='「」、「」'
    text=' 1 '
    strip = text.replace('*', '').strip()
    print("text_to_speech:", text)
    print("strip:", strip)
    if not strip: print("Error: No text to convert to speech."); return

    # strip='\t'
    try:
        tts = gtts.gTTS(strip, lang='zh-tw')
        tts_fp = io.BytesIO()
    
        tts.write_to_fp(tts_fp)
        tts_fp.seek(0) # Reset the file pointer to the beginning

        pygame.mixer.init()
        pygame.mixer.music.load(tts_fp, 'mp3')
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)  # Wait for the sound to finish playing   
    except Exception as e:
        print("text_to_speech:", text)
        print("Exception:", e)


# 測試用的語音
if __name__ == "__main__":
    unit_test()
