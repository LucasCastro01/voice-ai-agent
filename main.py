import time
import wave
import threading
import numpy as np
import sounddevice as sd
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
import os
from audio_source import MicrofoneSource, SAMPLE_RATE
from vad import VADBuffer
from config import audio_para_texto
from agent_react import perguntar_ia

load_dotenv()

elevenlabs = ElevenLabs(api_key=os.getenv("ELEVEN_LABS"))

ELEVENLABS_SAMPLE_RATE = 16000
GRACE_PERIOD_MS = 600  # ignora VAD nos primeiros 600ms após o agente começar a falar

agente_falando = threading.Event()  # True enquanto o agente está tocando áudio
parar_player   = threading.Event()  # sinaliza o player para parar

def tocar_audio(pcm_bytes: bytes):
    """Toca áudio PCM em chunks de 20ms — para imediatamente se parar_player for setado."""
    audio = np.frombuffer(pcm_bytes, dtype=np.int16)
    chunk = int(ELEVENLABS_SAMPLE_RATE * 0.02)

    with sd.OutputStream(samplerate=ELEVENLABS_SAMPLE_RATE, channels=1, dtype="int16") as stream:
        for i in range(0, len(audio), chunk):
            if parar_player.is_set():
                break
            stream.write(audio[i:i + chunk])


def falar(texto: str):
    audio_gen = elevenlabs.text_to_speech.convert(
        text=texto,
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        model_id="eleven_multilingual_v2",
        output_format="pcm_16000", 
    )
    pcm_bytes = b"".join(audio_gen)

    parar_player.clear()
    agente_falando.set()
    tocar_audio(pcm_bytes)
    agente_falando.clear()

def processar_fala(audio_fala: bytes):
    caminho_wav = _salvar_wav(audio_fala)
    texto = audio_para_texto(caminho_wav)
    print(f"\n🧑 Você disse: {texto}")

    if "sair" in texto.lower():
        print("👋 Encerrando...")
        parar_player.set()
        os._exit(0)

    print("🤖 Pensando...")
    resposta = perguntar_ia(texto=texto)
    print(f"🤖 IA: {resposta}")

    falar(resposta)
    print("\n🎤 Pode falar...")


def _salvar_wav(pcm: bytes) -> str:
    caminho = "audio_temp.wav"
    with wave.open(caminho, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm)
    return caminho

def main():
    source = MicrofoneSource()
    vad = VADBuffer(sample_rate=SAMPLE_RATE)
    grace_chunks = 0
    grace_iniciado = False

    source.iniciar()
    print("🎤 Pode falar... (diga 'sair' para encerrar)")

    try:
        while True:
            chunk = source.ler_chunk()
            if chunk is None:
                time.sleep(0.005)
                continue

            if agente_falando.is_set() and grace_chunks == 0 and not grace_iniciado:
                grace_chunks = int(GRACE_PERIOD_MS / 32)
                grace_iniciado = True

            if grace_chunks > 0:
                grace_chunks -= 1
                continue

            if not agente_falando.is_set():
                grace_iniciado = False
            audio_fala = vad.adicionar_chunk(chunk)

            if audio_fala:
                if agente_falando.is_set():
                    print("\n⚡ Interrompido!")
                    parar_player.set()

                threading.Thread(target=processar_fala, args=(audio_fala,), daemon=True).start()

    finally:
        source.parar()


if __name__ == "__main__":
    main()