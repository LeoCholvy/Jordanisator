from enum import Enum, auto
from typing import TypedDict, Literal


class ValState(Enum):
    NOT_STARTED = auto()
    PREGAME = auto()
    CORE_GAME = auto()

STATE = ValState.NOT_STARTED

class TypePlayer(TypedDict):
    puuid: str
    name: str | None
    tag: str | None
    team: Literal["ally", "enemy"] | None
    character: str | None
    mmr: int | None
    rank: str | None

class TypeMacthInfo(TypedDict):
    id: str | None
    map: str
    mode: str | None
    score: list[int] | None
    players: list[TypePlayer] | None
    nbRoundToWin: int | None

MATCH_INFO: TypeMacthInfo | None = None