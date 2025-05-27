import asyncio
import base64
import json
import os
import ssl
from pathlib import Path
import sys
import websockets
import pprint
from json_to_struct import get_structure_from_json
import logging

LOCKFILE_PATHS = [
    Path(os.getenv('LOCALAPPDATA', '')) / "Riot Games" / "Riot Client" / "Config" / "lockfile",
    Path(os.getenv('LOCALAPPDATA', '')) / "Riot Games" / "Beta" / "Config" / "lockfile",
]

SUBSCRIBE_MSG = '[5, "OnJsonApiEvent"]'
TIMEOUT_SECONDS = 60 * 5  # 5 minutes

EVENTS = []
EVENTS_TYPES = {}
# EVENTS_STRUCT = []

class LockfileNotFound(Exception):
    pass
def parse_lockfile() -> dict:
    for path in LOCKFILE_PATHS:
        if path.exists():
            parts = path.read_text().strip().split(':')
            # print("LockFile:", parts)
            logging.info("LockFile: %s", parts)
            return {
                'process_name': parts[0],
                'pid'         : parts[1],
                'port'        : parts[2],
                'password'    : parts[3],
                'protocol'    : parts[4],
            }
    raise LockfileNotFound("Aucun lockfile Riot trouvé. Le jeu ne semble pas lancé.")
from json_to_struct import get_structure_from_json
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
                    try:
                        msg = await ws.recv()
                        arr = json.loads(msg)
                        if not (isinstance(arr, list) and len(arr) >= 3 and isinstance(arr[2], dict) and arr[1] == 'OnJsonApiEvent'):
                            # print("WTF:", msg, '-----------------')
                            logging.warning("Message inattendu reçu : %s", msg)
                            continue
                        payload = arr[2]
                        if payload.get('data') is None:
                            # print("Aucun data dans le message :", msg)
                            logging.warning("Aucun 'data' dans le message : %s", msg)
                            continue
                        EVENTS.append(payload)
                        msg_type = (arr[0], arr[1], payload.get('eventType'), payload.get('uri'), '|'.join(list(payload.get('data').keys())))
                        msg_type = [str(x) for x in msg_type if x is not None]
                        msg_type = ' | '.join(msg_type)
                        if msg_type not in EVENTS_TYPES:
                            event_structure = get_structure_from_json(payload.get('data'))
                            EVENTS_TYPES[msg_type] = event_structure
                            # print(msg_type)
                            logging.info("Nouveau type d'événement : %s", msg_type)
                            # pprint(get_structure_from_json(payload.get('data')))
                            logging.info("Structure de l'événement : %s", pprint.pformat(get_structure_from_json(payload.get('data'))))
                            logging.info('\n\n')
                    except Exception as e:
                        print(e)
                        # print("Erreur lors de la réception du message :", msg)
                        logging.error("Erreur lors de la réception du message : %s", msg)
        except asyncio.TimeoutError:
            # print(f"Timeout de {TIMEOUT_SECONDS} secondes atteint. Fin de l'écoute.")
            logging.CRITICAL("Timeout de %d secondes atteint. Fin de l'écoute.", TIMEOUT_SECONDS)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
    try:
        asyncio.run(listen_for_event())
    except KeyboardInterrupt:
        logging.info("Écoute interrompue par l'utilisateur.")
    # with open('events_log_raw.json', 'w') as f:
    #     json.dump([EVENTS, EVENTS_TYPES], f, indent=4)
    # pprint.pprint(EVENTS_TYPES)
    # logging.info("Événements enregistrés dans 'events_log_raw.json'.")