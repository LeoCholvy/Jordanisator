import asyncio
import logging

from webSocketHandler import WebSocketHandler
import globalState

logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
)

async def main():
    wsh = WebSocketHandler()
    logging.info("Démarrage de l'application...")
    # asyncio.create_task(wsh.listen_for_event())
    print(wsh.getPresence())
    while True:
        logging.debug("ping...")
        await asyncio.sleep(10)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Application arrêtée par l'utilisateur.")