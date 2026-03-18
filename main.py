from config import gravar_audio, audio_para_texto, engine
from websocket import create_connection

ws = create_connection("ws://localhost:8000/ws")

def falar(texto):
    engine.stop()
    engine.say(texto)
    engine.runAndWait()

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