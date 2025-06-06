import asyncio
import base64
import json
import logging
import os
import ssl
from pathlib import Path

import requests
import websockets

from events import onPresenceUpdate, decodePresence
from events import ValState, onAresUpdate, onHeartbeatUpdate
import globalState

instance = None

LOCKFILE_PATHS = [
    Path(os.getenv('LOCALAPPDATA', '')) / "Riot Games" / "Riot Client" / "Config" / "lockfile",
    Path(os.getenv('LOCALAPPDATA', '')) / "Riot Games" / "Beta" / "Config" / "lockfile",
]

SUBSCRIBE_MSG = '[5, "OnJsonApiEvent"]'

presence_state = {
    "PREGAME": ValState.PREGAME,
    "MENUS": ValState.MENUS,
    "INGAME": ValState.CORE_GAME,
}

class LockfileNotFound(Exception):
    pass

class WebSocketHandler:
    task_presence = None

    def __init__(self):
        self.lockfile = self.parse_lockfile()
        self.uri = uri = f"wss://127.0.0.1:{self.lockfile['port']}/"
        basic_auth_token = auth_token = base64.b64encode(f"riot:{self.lockfile['password']}".encode()).decode()
        self.basic_headers = {"Authorization": f"Basic {basic_auth_token}"}
        logging.debug("WebSocket initialized with URI: %s", uri)
        global instance
        instance = self

    def parse_lockfile(self) -> dict:
        for path in LOCKFILE_PATHS:
            if path.exists():
                parts = path.read_text().strip().split(':')
                logging.info("LockFile: %s", parts)
                return {
                    'process_name': parts[0],
                    'pid'         : parts[1],
                    'port'        : parts[2],
                    'password'    : parts[3],
                    'protocol'    : parts[4],
                }
        raise LockfileNotFound("Aucun lockfile Riot trouvé. Le jeu ne semble pas lancé.")

    async def handleEvent(self, payload):
        try:
            event_type = payload.get('eventType')
            uri = payload.get('uri')
            data = payload.get('data')
            if uri.startswith('/riot-messaging-service/v1/message/ares-pregame/pregame') or uri.startswith('/riot-messaging-service/v1/message/ares-core-game/core-game'):
                onAresUpdate()
            elif uri.startswith('/product-session/v1/session-heartbeats'):
                onHeartbeatUpdate()
            elif uri.startswith('/chat/v4/presences'):
                onPresenceUpdate(self.format_presence_responce(data))


        except Exception as e:
            logging.error("Error handling event: %s", e)

    async def listen_for_event(self):
        # Desable SSL verification to accept self-signed certificate from Riot Client
        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE

        # Connect to the WebSocket server
        while True:
            try:
                ws = await websockets.connect(
                    self.uri,
                    ssl=ssl_ctx,
                    origin="https://127.0.0.1",
                    additional_headers=self.basic_headers,
                )
                logging.info("WebSocket connection established.")
                # Subscribe to events
                await ws.send(SUBSCRIBE_MSG)
                await ws.send(SUBSCRIBE_MSG)

                # Listen for events
                while True:
                    msg = await ws.recv()
                    try:
                        arr = json.loads(msg)
                        payload = arr[2]
                        asyncio.create_task(self.handleEvent(payload))
                    except:
                        logging.debug("Error processing message: %s", msg)
            except Exception as e:
                logging.debug("WebSocket connection error: %s", e)
                logging.error("WebSocket connection failed, client may not be running, retrying in 3 seconds...")
                globalState.STATE = ValState.NOT_STARTED
                await asyncio.sleep(3)

    async def request_presence(self) -> dict:
        url = f"https://127.0.0.1:{self.lockfile['port']}/chat/v4/presences"

        await asyncio.sleep(0.2)

        try:
            response = requests.get(url, headers=self.basic_headers, verify=False)
            response.raise_for_status()
            data = response.json()
            privates = self.format_presence_responce(data)
            decodePresence(privates)
        except Exception as e:
            logging.error("Error fetching presence: %s", e)

    async def get_presence(self) -> dict:
        if self.task_presence is None or self.task_presence.done():
            self.task_presence = asyncio.create_task(self.request_presence())
        decodePresence()

    @staticmethod
    def format_presence_responce(data):
        try:
            privates = {}
            for p in data.get('presences'):
                privates[p['puuid']] = json.loads(base64.b64decode(p['private']).decode('utf-8'))
                privates[p['puuid']]['game_name'] = p['game_name']
                privates[p['puuid']]['game_tag'] = p['game_tag']

            return privates
        except Exception as e:
            logging.error("Error formatting presence response: %s", e)
            return {}

    def request_session(self):
#         return {
#     "federated": True,
#     "game_name": "Basiloukoum",
#     "game_tag": "14ans",
#     "loaded": True,
#     "name": "",
#     "pid": "757372ab-6d7a-5b8c-932e-b19b8764ecae@eu2.pvp.net",
#     "puuid": "757372ab-6d7a-5b8c-932e-b19b8764ecae",
#     "region": "eu2",
#     "resource": "RC-2266017937",
#     "state": "connected"
# }
        url = f"https://127.0.0.1:{self.lockfile['port']}/chat/v1/session"

        response = requests.get(url, headers=self.basic_headers, verify=False)
        response.raise_for_status()
        data = response.json()
        return data