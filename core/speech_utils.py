import whisper
import sounddevice as sd
import numpy as np
import tempfile
import scipy.io.wavfile

from config.settings import settings


class SpeechUtils:
    """语音处理工具类"""

    def __init__(self):
        self.whisper_model = whisper.load_model(settings.WHISPER_MODEL)
        self.sample_rate = settings.SAMPLE_RATE

    def record_audio(self, duration: int = None) -> str:
        """录制音频"""
        if duration is None:
            duration = settings.RECORD_DURATION

        print(f"开始录音...（{duration}秒）")
        audio = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype='int16'
        )
        sd.wait()
        print("录音结束")

        # 保存为临时文件
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        scipy.io.wavfile.write(temp_file.name, self.sample_rate, audio)
        return temp_file.name

    def speech_to_text(self, audio_path: str) -> str:
        """语音转文本"""
        try:
            result = self.whisper_model.transcribe(audio_path, fp16=False, language="zh")
            return result["text"].strip()
        except Exception as e:
            print(f"语音识别错误: {e}")
            return ""