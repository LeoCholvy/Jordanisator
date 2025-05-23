import os
from pathlib import Path


LOCKFILE_PATHS = [
    Path(os.getenv('LOCALAPPDATA', '')) / "Riot Games" / "Riot Client" / "Config" / "lockfile",
    Path(os.getenv('LOCALAPPDATA', '')) / "Riot Games" / "Beta" / "Config" / "lockfile",
]

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