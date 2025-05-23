from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import threading
from typing import Set
import uvicorn

app = FastAPI()

# Configuration CORS pour permettre les connexions depuis React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # URL de ton app React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Stockage des connexions WebSocket actives
active_connections: Set[WebSocket] = set()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        print(f"Connexion établie. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        print(f"Connexion fermée. Total: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        """Envoie un message à toutes les connexions actives"""
        if self.active_connections:
            # Copie la liste pour éviter les modifications pendant l'itération
            connections_copy = self.active_connections.copy()
            for connection in connections_copy:
                try:
                    await connection.send_text(message)
                except:
                    # Supprime les connexions fermées
                    self.active_connections.discard(connection)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Garde la connexion ouverte
        while True:
            # Attend les messages du client (optionnel)
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

def input_loop():
    """Boucle pour demander des entrées utilisateur dans un thread séparé"""
    print("Logger démarré! Tapez vos messages (Ctrl+C pour quitter):")
    try:
        while True:
            user_input = input(">>> ")
            if user_input.strip():
                # Utilise asyncio pour envoyer le message
                asyncio.run_coroutine_threadsafe(
                    manager.broadcast(f"[LOG] {user_input}"),
                    loop
                )
    except KeyboardInterrupt:
        print("\nArrêt du logger...")

@app.on_event("startup")
async def startup_event():
    global loop
    loop = asyncio.get_event_loop()

    # Démarre la boucle d'input dans un thread séparé
    input_thread = threading.Thread(target=input_loop, daemon=True)
    input_thread.start()

    print("Serveur FastAPI démarré sur http://localhost:8000")
    print("WebSocket disponible sur ws://localhost:8000/ws")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)