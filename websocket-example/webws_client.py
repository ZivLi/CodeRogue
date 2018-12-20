import asyncio
import websockets

async def hello():
    async with websockets.connect('ws://localhost:8000') as websocket:
        input_name = input("Please input your name")

        await websocket.send(input_name)
        print(f"> {input_name}")

        greeting = await websocket.recv()
        print(f"< {greeting}")

async def not_goodbye_name():
    async with websockets.connect('ws://localhost:8000/goodbye') as wbs:
        user_id, user_name = 4000, 'xxxx'

        await wbs.send(user_id, user_name)
        

# asyncio.get_event_loop().run_until_complete(hello())