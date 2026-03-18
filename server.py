import websocket
from config import gravar_audio, audio_para_texto

ws = websocket.WebSocket()
ws.connect("ws://localhost:8000/ws")

while True:
    texto = gravar_audio()

    ws.send(texto)

    resposta = ws.recv()
    audio_para_texto(resposta)