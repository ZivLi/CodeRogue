import asyncio
import websockets

async def hello(websockets, path):
    name = await websockets.recv()
    if name == 'ziv':
        print(f"< {name}")

        print(path)
        greeting = f"Hello {name}!"

        await websockets.send(greeting)
        print(f"> {greeting}")
    else:
        await goodbye(websockets, name)

async def goodbye(websockets, name):
    print(f"<<<<<<{name}")
    await websockets.send('close please')



start_server = websockets.serve(hello, 'localhost', 8000)
# bye_server = websockets.serve(goodbye, 'localhost', 8000)

asyncio.get_event_loop().run_until_complete(start_server)
# asyncio.get_event_loop().run_until_complete(bye_server)

asyncio.get_event_loop().run_forever()