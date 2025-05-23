import asyncio
import base64
import json
import os
import ssl
from pathlib import Path
import sys

import websockets

LOCKFILE_PATHS = [
    Path(os.getenv('LOCALAPPDATA', '')) / "Riot Games" / "Riot Client" / "Config" / "lockfile",
    Path(os.getenv('LOCALAPPDATA', '')) / "Riot Games" / "Beta" / "Config" / "lockfile",
]

SUBSCRIBE_MSG = '[5, "OnJsonApiEvent"]'
TIMEOUT_SECONDS = 120

PRES = []

class LockfileNotFound(Exception):
    pass
def parse_lockfile() -> dict:
    for path in LOCKFILE_PATHS:
        if path.exists():
            parts = path.read_text().strip().split(':')
            print("LockFile:", parts)
            return {
                'process_name': parts[0],
                'pid'         : parts[1],
                'port'        : parts[2],
                'password'    : parts[3],
                'protocol'    : parts[4],
            }
    raise LockfileNotFound("Aucun lockfile Riot trouvé. Le jeu ne semble pas lancé.")

async def listen_for_event():
    # 1) Lecture du lockfile
    try:
        lf = parse_lockfile()
    except LockfileNotFound as e:
        print(e)
        sys.exit(1)

    # 3) Sinon abonnement WebSocket
    uri = f"wss://127.0.0.1:{lf['port']}/"
    ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE

    auth_token = base64.b64encode(f"riot:{lf['password']}".encode()).decode()
    headers = {"Authorization": f"Basic {auth_token}"}

    try:
        async with websockets.connect(
            uri,
            subprotocols=["wamp"],
            ssl=ssl_ctx,
            origin="https://127.0.0.1",
            additional_headers=headers
        ) as ws:
            await ws.send(SUBSCRIBE_MSG)
            await ws.send(SUBSCRIBE_MSG)

            try:
                async with asyncio.timeout(TIMEOUT_SECONDS):
                    while True:
                        msg = await ws.recv()
                        arr = json.loads(msg)
                        if not (isinstance(arr, list) and len(arr) >= 3 and isinstance(arr[2], dict)):
                            continue
                        payload = arr[2]
                        if type(payload) != dict:
                            print("Payload invalide :", payload)
                            continue
                        if payload.get('data').get('ackRequired') != None:
                            continue
                        print("Payload reçu :", payload.get('data').keys())
                        if payload.get('data').get('presences'):
                            PRES.append(payload.get('data').get('presences'))
                        if payload.get('data').get('phase'):
                            print("Payload de phase :", payload.get('data').get('phase'))
                        # if payload.get('data').get('friends'):
                        #     print("Payload d'amis :", payload.get('data').get('friends'))
            except asyncio.TimeoutError:
                print(f"Aucun événement de présence reçu sous {TIMEOUT_SECONDS}s. Aucune partie en cours.")
            except Exception:
                print("Erreur lors de la réception du message :", msg)
    except Exception as e:
        print("Erreur de connexion au WebSocket :", e)
        sys.exit(1)
    except KeyboardInterrupt as e:
        print("Interruption du programme :", e)

if __name__ == "__main__":
    asyncio.run(listen_for_event())
    print(PRES)