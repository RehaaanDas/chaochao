import websockets
import asyncio

connections = set()

async def handler(websocket):
    connections.add(websocket)
    print(f"{websocket.remote_address} connected")

    async for msg in websocket:
        websockets.broadcast(connections, msg)
async def main():
    async with websockets.serve(handler, "0.0.0.0", 8002):
        print("server@ws://0.0.0.0:8002")
        await asyncio.Future()

asyncio.run(main())