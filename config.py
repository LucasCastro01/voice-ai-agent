import sounddevice as sd
from scipy.io.wavfile import write
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def gravar_audio(nome_arquivo="audio.wav", duracao=5, fs=16000):
    print("🎤 Fale agora...")
    audio = sd.rec(int(duracao * fs), samplerate=fs, channels=1)
    sd.wait()
    write(nome_arquivo, fs, audio)
    print("✅ Áudio gravado!")
    return nome_arquivo


def audio_para_texto(caminho_audio):
    with open(caminho_audio, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=file,
            model="whisper-large-v3",
            language="pt",
        )
    return transcription.text