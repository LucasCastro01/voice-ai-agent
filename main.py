from config import gravar_audio, audio_para_texto
from websocket import create_connection
from elevenlabs.client import ElevenLabs
import os
from dotenv import load_dotenv

load_dotenv()

ws = create_connection("ws://localhost:8000/ws")

elevenlabs  = ElevenLabs(api_key=os.getenv("ELEVEN_LABS"))

def falar(texto):
    audio = elevenlabs.text_to_speech.convert(
        text=texto,
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )

    return audio


def main():
    while True:
        audio = gravar_audio()

        texto = audio_para_texto(audio)
        print("🧑 Você disse:", texto)

        ws.send(texto)

        resposta = ws.recv()
        print("🤖 IA:", resposta)

        falar(resposta)

        if "sair" in texto.lower():
            break

if __name__ == "__main__":
    main()