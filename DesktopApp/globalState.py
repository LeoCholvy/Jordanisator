from enum import Enum, auto
from typing import TypedDict, Literal


class ValState(Enum):
    NOT_STARTED = "not-started"
    MENUS = "MENU"
    PREGAME = "PREGAME"
    CORE_GAME = "INGAME"


class TypePlayer(TypedDict):
    puuid: str
    name: str | None
    tag: str | None
    team: Literal["ally", "enemy"] | None
    character: str | None
    mmr: int | None
    rr: int | None
    rankTier: int | None
    lvl: int | None

class TypeMacthInfo(TypedDict):
    id: str | None
    map: str
    mode: str | None
    score: list[int] | None
    players: list[TypePlayer] | None
    nbRoundToWin: int | None


STATE = ValState.NOT_STARTED
MATCH_INFO: TypeMacthInfo | None = None
USER_PLAYER_INFO = None

def isMatchInfoComplete() -> bool:
    global MATCH_INFO
    if MATCH_INFO is None:
        return False
    for v in MATCH_INFO.values():
        if v is None:
            return False