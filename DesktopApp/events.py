import asyncio
import logging
from enum import Enum
from pprint import pprint
from typing import TypedDict

import globalState
import webSocketHandler
from globalState import isMatchInfoComplete, TypeMacthInfo
from idDecoder import decodeMap


class ValState(Enum):
    NOT_STARTED = "not-started"
    MENUS = "menus"
    PREGAME = "pregame"
    CORE_GAME = "core-game"

class MacthInfo(TypedDict):
    id: str



# def onGameStart(private):
#     # Check if the game is starting
#     if globalState.STATE != ValState.CORE_GAME:
#         globalState.STATE = ValState.CORE_GAME
#         logging.warning("Game started.")
#
#     # Check if we are already in a match
#     if globalState.MATCH_INFO is None:
#         logging.warning("Already in a match !")
#         globalState.STATE = ValState.PREGAME
#         logging.warning("Pregame started.")
#         globalState.MATCH_INFO = globalState.TypeMacthInfo(
#             map=decodeMap(private.get('partyOwnerMatchMap', "Unknown Map")),
#             mode=None,
#             score=[0, 0],
#             players=None,
#             id=None,
#             nbRoundToWin=None
#         )
#         logging.warning("Map: %s", globalState.MATCH_INFO['map'])
#         globalState.MATCH_INFO['mode'] = private.get('provisioningFlow', "Unknown Mode")
#         logging.warning("Mode: %s", globalState.MATCH_INFO['mode'])
#
#     # Update score
#     score = [
#         private.get('partyOwnerMatchScoreAllyTeam', 0),
#         private.get('partyOwnerMatchScoreEnemyTeam', 0)
#     ]
#     if globalState.MATCH_INFO.get('score') is None:
#         globalState.MATCH_INFO['score'] = score
#     else:
#         if globalState.MATCH_INFO['score'] != score:
#             globalState.MATCH_INFO['score'] = score
#             logging.warning("Score updated: %s", globalState.MATCH_INFO['score'])
#             # TODO check side switch
#     if private.get('provisioningFlow') not in (None, "Invalid", "Matchmaking") and globalState.MATCH_INFO['mode'] != private.get('provisioningFlow'):
#         globalState.MATCH_INFO['mode'] = private.get('provisioningFlow', "Unknown Mode")
#         logging.warning("Mode: %s", globalState.MATCH_INFO['mode'])
# def onSideSwitch():
#     pass
#
# def onPregameStart(private):
#     if globalState.STATE != ValState.PREGAME:
#         globalState.STATE = ValState.PREGAME
#         logging.warning("Pregame started.")
#         globalState.MATCH_INFO = globalState.TypeMacthInfo(
#             map=decodeMap(private.get('partyOwnerMatchMap', "Unknown Map")),
#             mode=None,
#             score=[0, 0],
#             players=None,
#             id=None,
#             nbRoundToWin=None
#         )
#         logging.warning("Map: %s", globalState.MATCH_INFO['map'])
# def onMenu():
#     if globalState.STATE != ValState.MENUS:
#         globalState.STATE = ValState.MENUS
#         globalState.MATCH_INFO = None
#         logging.warning("Back to menus")

def onPresenceUpdate(pres):
    decodePresence(pres)

def onAresUpdate():
    # webSocketHandler.instance.request_presence()
    asyncio.create_task(webSocketHandler.instance.request_presence())
def onHeartbeatUpdate():
    asyncio.create_task(webSocketHandler.instance.request_presence())


def updateMatchInfo(user_presence):
    try:
        # MAP
        map = decodeMap(user_presence.get('matchMap'))
        if globalState.MATCH_INFO is None:
            globalState.MATCH_INFO = TypeMacthInfo(map=map)
        else:
            globalState.MATCH_INFO['map'] = map
        # TODO: ID
        # MODE
        # TODO : decode it (can be Invalid or else) (do we need to get it from the server API ?)
        # TODO : get the number of round to win
        globalState.MATCH_INFO['mode'] = user_presence.get('provisioningFlow')
        # Score
        if globalState.STATE == ValState.CORE_GAME:
            score = [
                user_presence.get('partyOwnerMatchScoreAllyTeam', 0),
                user_presence.get('partyOwnerMatchScoreEnemyTeam', 0)
            ]
            globalState.MATCH_INFO['score'] = score

        # TODO: get all the player of the game infos (maybe need to do a new request

    except Exception as e:
        logging.error(e)
        return


def decodePresence(pres):
    puuid = globalState.USER_PLAYER_INFO.get('puuid')
    print(puuid)
    user_presence = pres.get(puuid)

    # Update STATE
    newState:bool = checkStateFromPresence(user_presence.get('sessionLoopState'))
    if newState or not isMatchInfoComplete():
        updateMatchInfo(user_presence)

def checkStateFromPresence(sessionLoopState) -> bool:
    if sessionLoopState is None:
        return False
    if sessionLoopState == globalState.STATE:
        return False
    if sessionLoopState == ValState.MENUS:
        globalState.STATE = ValState.MENUS
        return False
    elif sessionLoopState == ValState.PREGAME:
        if globalState.STATE == ValState.PREGAME:
            return False
        globalState.STATE = ValState.PREGAME
        return True
    elif sessionLoopState == ValState.CORE_GAME:
        if globalState.STATE == ValState.CORE_GAME:
            return False
        globalState.STATE = ValState.CORE_GAME
        return True

    return False