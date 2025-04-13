import vosk
import pyaudio
import json

# 關閉 Vosk debug output
vosk.SetLogLevel(-1)

# 載入 Vosk 模型
print("載入 Vosk 模型...")
VOSK_MODEL_PATH = "vosk_models/vosk-model-small-cn-0.22"
model = vosk.Model(VOSK_MODEL_PATH)
rec = vosk.KaldiRecognizer(model, 16000)

# 初始化 PyAudio
audio = pyaudio.PyAudio()


def listen():
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4096)
    stream.start_stream()

    while True:
        data = stream.read(4096, exception_on_overflow=False)
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            # print('1:',result)
            break
        # else:
        #     partial_result = rec.PartialResult()
        #     print('2:', partial_result)

    stream.stop_stream()
    stream.close()

    return result["text"]

def unit_test():
    print("請說話...")
    while True:
        command = listen()
        print("辨識結果:", command)


if __name__ == "__main__":
    unit_test()
