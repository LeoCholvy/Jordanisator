#!/usr/bin/env python3
import os
import sys
import json
import ssl
import base64
import asyncio
import websockets
import requests
from pathlib import Path

# Dictionnaire de traduction map-path ➡️ nom visible
MAP_NAME_MAPPING = {
    "/Game/Maps/Ascent/Ascent": "Ascent",
    "/Game/Maps/Duality/Duality": "Bind",
    "/Game/Maps/Foxtrot/Foxtrot": "Breeze",
    "/Game/Maps/Canyon/Canyon": "Fracture",
    "/Game/Maps/Triad/Triad": "Haven",
    "/Game/Maps/Port/Port": "Icebox",
    "/Game/Maps/Pitt/Pitt": "Pearl",
    "/Game/Maps/Juliett/Juliett": "Sunset",   # <— Juliett = Sunset
    "/Game/Maps/Jam/Jam": "Lotus",
    "/Game/Maps/Bonsai/Bonsai": "Split",
    "/Game/Maps/Infinity/Infinity": "Abyss",
    "/Game/Maps/HURM/HURM_Yard/HURM_Yard": "Piazza",
    "/Game/Maps/HURM/HURM_Bowl/HURM_Bowl": "Kasbah",
    "/Game/Maps/HURM/HURM_HighTide/HURM_HighTide": "Glitch",
    "/Game/Maps/HURM/HURM_Helix/HURM_Helix": "Drift",
    "/Game/Maps/HURM/HURM_Alley/HURM_Alley": "District",
    # ajoute ici d'autres si besoin
}

LOCKFILE_PATHS = [
    Path(os.getenv('LOCALAPPDATA', '')) / "Riot Games" / "Riot Client" / "Config" / "lockfile",
    Path(os.getenv('LOCALAPPDATA', '')) / "Riot Games" / "Beta" / "Config" / "lockfile",
]

SUBSCRIBE_MSG = '[5, "OnJsonApiEvent"]'
TIMEOUT_SECONDS = 120

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

def fetch_current_presence(lf: dict) -> dict | None:
    """Interroge l'API REST locale pour obtenir la présence actuelle."""
    url = f"https://127.0.0.1:{lf['port']}/chat/v4/presences"
    try:
        resp = requests.get(url, auth=('riot', lf['password']), verify=False, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        pres = data.get('presences', [])
        return pres[0] if pres else None
    except Exception as e:
        print("⚠️  Impossible d'appeler l'API REST locale :", e)
        return None

def decode_private(raw: str) -> dict:
    try:
        return json.loads(base64.b64decode(raw).decode())
    except Exception:
        return {}

def human_map_name(map_path: str) -> str:
    return MAP_NAME_MAPPING.get(map_path, map_path)

def fetch_agent_and_team(lf: dict):
    # Toujours définir headers en amont
    auth_str = f"riot:{lf['password']}"
    auth_b64 = base64.b64encode(auth_str.encode()).decode()
    headers = {'Authorization': f'Basic {auth_b64}'}

    # 1. Tentative via core-game (quand la game a démarré)
    session_url = f"https://127.0.0.1:{lf['port']}/core-game/v1/session"
    try:
        session_resp = requests.get(session_url, headers=headers, verify=False)
        session_resp.raise_for_status()
        match_id = session_resp.json()["MatchID"]

        player_url = f"https://127.0.0.1:{lf['port']}/core-game/v1/players/{match_id}"
        players_resp = requests.get(player_url, headers=headers, verify=False)
        players_resp.raise_for_status()
        data = players_resp.json()

        for player in data["Players"]:
            if player["Subject"] == data["LocalPlayer"]:
                agent = player["CharacterID"]
                team  = player["TeamID"]
                return agent, team

    except Exception as e:
        print("Erreur lors de la récupération agent/équipe :", e)

    # 2. Tentative via pregame (sélection des agents en cours)
    try:
        pregame_resp = requests.get(f"https://127.0.0.1:{lf['port']}/pregame/v1/session", headers=headers, verify=False)
        pregame_resp.raise_for_status()
        data = pregame_resp.json()

        local_player = data["Subject"]
        team_id = None
        character_id = None

        for player in data.get("AllyTeam", {}).get("Players", []):
            if player["Subject"] == local_player:
                character_id = player.get("CharacterID")
                team_id = data["AllyTeam"].get("TeamID")
                break

        if character_id and team_id:
            return character_id, team_id

    except Exception as e:
        print("⚠️  Erreur PREGAME:", e)

    return None





async def get_current_game_type():
    # 1) Lecture du lockfile
    try:
        lf = parse_lockfile()
    except LockfileNotFound as e:
        print(e)
        sys.exit(1)

    # 2) Interroga REST pour état immédiat
    pres0 = fetch_current_presence(lf)
    if pres0:
        priv = decode_private(pres0.get('private', ''))
        state  = priv.get('sessionLoopState', 'UNKNOWN')
        custom = priv.get('customGameName') or priv.get('queueId') or "(non renseigné)"
        mapraw = priv.get('matchMap', 'UNKNOWN')
        print(">> Via REST API :")
        print("État de la session :", state)
        print("Type de partie     :", custom)
        print("Carte              :", human_map_name(mapraw))
        # return

    pregame_url = f"https://127.0.0.1:{lf['port']}/pregame/v1/session"
    try:
        resp = requests.get(pregame_url, headers=headers, verify=False)
        if resp.status_code == 200:
            print("✅ PREGAME session accessible.")
            print(json.dumps(resp.json(), indent=2))
        else:
            print(f"❌ PREGAME status: {resp.status_code}")
    except Exception as e:
        print("⚠️  Erreur PREGAME:", e)
    pres1 = fetch_agent_and_team(lf)
    if pres1:
        print(">> Infos joueur :")
        print("Agent             :", pres1[0])
        print("Équipe (TeamID)   :", pres1[1])
    else:
        print("⚠️  Impossible de déterminer l'agent ou l'équipe.")

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

                        if payload.get('uri', '').endswith("/chat/v4/presences"):
                            pres_list = payload.get('data', {}).get('presences', [])
                            if not pres_list:
                                continue
                            priv = decode_private(pres_list[0].get('private', ''))
                            print(priv, "\n")
                            state  = priv.get('sessionLoopState', 'UNKNOWN')
                            custom = priv.get('customGameName') or priv.get('queueId') or "(non renseigné)"
                            mapraw = priv.get('matchMap', 'UNKNOWN')
                            team = priv.get('customGameTeam') or priv.get('partyOwnerMatchCurrentTeam') or 'UNKNOWN'
                            print(">> Via WebSocket :")
                            print("État de la session :", state)
                            print("Type de partie     :", custom)
                            print("Carte              :", human_map_name(mapraw))
                            print("Equipe             :", team)
            except asyncio.TimeoutError:
                print(f"Aucun événement de présence reçu sous {TIMEOUT_SECONDS}s. Aucune partie en cours.")
    except Exception as e:
        print("Erreur de connexion au WebSocket :", e)
        sys.exit(1)

# if __name__ == "__main__":
#     import urllib3; urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#     asyncio.run(get_current_game_type())
print(parse_lockfile())