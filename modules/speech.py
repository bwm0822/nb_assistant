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