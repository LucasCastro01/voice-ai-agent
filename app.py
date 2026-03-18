from fastapi import FastAPI, WebSocket
from agent_react import perguntar_ia

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()

    while True:
        texto = await ws.receive_text()
        response = perguntar_ia(texto=texto)
        await ws.send_text(response)