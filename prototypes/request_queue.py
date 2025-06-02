import asyncio

DELAY = 0.2  # délai d'attente pour accumuler les requêtes
_task: asyncio.Task | None = None  # tâche en cours pour f1

async def f1():
    # Attendre un petit délai pour accumuler les appels
    await asyncio.sleep(DELAY)
    # Effectuer ici le travail réel et retourner le résultat
    result = "résultat de f1"
    print("Travail réel de f1")
    return result

async def f2():
    global _task
    # Si aucune tâche n'est en cours ou si la tâche précédente est terminée,
    # créer une nouvelle tâche pour f1
    if _task is None or _task.done():
        _task = asyncio.create_task(f1())
    # Tous les appels à f2 attendent le même résultat
    return await _task

# Exemple d'utilisation: appel de f2 plusieurs fois depuis le thread principal
async def main():
    # Démarrer quelques appels à f2 presque simultanément
    results = await asyncio.gather(f2(), f2(), f2())
    for idx, res in enumerate(results):
        print(f"f2[{idx}] a reçu :", res)

if __name__ == "__main__":
    asyncio.run(main())