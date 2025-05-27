import logging
from enum import Enum
from pprint import pprint
from typing import TypedDict

import globalState
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

def onPresenceUpdate(private):
    pass
def onAresUpdate():
    pass
def onHeartbeatUpdate():
    pass