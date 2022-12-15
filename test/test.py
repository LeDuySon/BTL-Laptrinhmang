import asyncio 
import websockets
import json

data = {
    "result": 2,
    "match": 1,
    "status": 1
}

async def hello(data):
    async with websockets.connect("ws://104.194.240.16/ws/channels/") as websocket:
        await websocket.send(json.dumps(data))
        msg = await websocket.recv()
        print(msg)

def run(data):
    asyncio.run(hello(data))
    
run(data)
        