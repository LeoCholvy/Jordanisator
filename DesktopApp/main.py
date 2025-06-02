import asyncio
import logging

from events import onPresenceUpdate
from globalState import TypePlayer, ValState
from webSocketHandler import WebSocketHandler
import globalState

logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
)


def init_user_info(wsh):
    while True:
        try:
            data = wsh.request_session()
            info = TypePlayer(
                puuid = data.get('puuid'),
                name = data.get('game_name'),
                tag = data.get('game_tag'),
                team = 'ally'
            )
            globalState.USER_PLAYER_INFO = info
            globalState.STATE = ValState.PREGAME
            return
        except Exception as e:
            logging.info("Failed to fetch user data")
        asyncio.sleep(3)


async def main():
    wsh = WebSocketHandler()
    logging.info("Démarrage de l'application...")
    init_user_info(wsh)
    # asyncio.create_task(wsh.listen_for_event())
#     onPresenceUpdate({
#   "757372ab-6d7a-5b8c-932e-b19b8764ecae": {"isValid": True, "sessionLoopState": "INGAME", "partyOwnerSessionLoopState": "INGAME", "customGameName": "", "customGameTeam": "TeamOne", "partyOwnerMatchMap": "/Game/Maps/Foxtrot/Foxtrot", "partyOwnerMatchCurrentTeam": "", "partyOwnerMatchScoreAllyTeam": 0, "partyOwnerMatchScoreEnemyTeam": 0, "partyOwnerProvisioningFlow": "CustomGame", "provisioningFlow": "CustomGame", "matchMap": "/Game/Maps/Foxtrot/Foxtrot", "partyId": "6ef2cf5c-039b-46a2-94f5-7b9dbe0dd405", "isPartyOwner": True, "partyState": "CUSTOM_GAME_SETUP", "partyAccessibility": "CLOSED", "maxPartySize": 12, "queueId": "", "partyLFM": False, "partyClientVersion": "release-10.09-shipping-3-3470802", "partySize": 1, "tournamentId": "", "rosterId": "", "partyVersion": 1748091324817, "queueEntryTime": "2025.05.24-12.40.03", "playerCardId": "4202d7d4-4a0d-3f36-4eb7-c9b40ffe9acf", "playerTitleId": "", "preferredLevelBorderId": "", "accountLevel": 16, "competitiveTier": 0, "leaderboardPosition": 0, "isIdle": False, "tempValueX": "", "tempValueY": "", "tempValueZ": False, "tempValueW": False, "tempValueV": 1, "premierPresenceData": {"rosterId": "", "rosterName": "", "rosterTag": "", "division": 0, "score": 0, "tempValueA": 0, "tempValueB": False, "tempValueC": False, "tempValueD": False}}
# })
    # while True:
    #     # TODO: ping the API and reinit if it deconnect
    #     logging.debug("ping...")
    #     await asyncio.sleep(10)
    # print(globalState.STATE)
    # print(globalState.MATCH_INFO)
    # print(globalState.USER_PLAYER_INFO)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Application arrêtée par l'utilisateur.")