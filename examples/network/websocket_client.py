import asyncio
import websockets
import time

async def send_msg(websocket):
    count = 1
    while count <= 10:
        msg = f"hello {count}"
        await websocket.send(msg)
        recv_text = await websocket.recv()
        print(f"receive: {recv_text}", end="\n")
        count += 1
        time.sleep(1)
    await websocket.close(reason="client exit")

async def main_logic(ip, port):
    async with websockets.connect(f'ws://{ip}:{port}') as websocket:
        await send_msg(websocket)

ip = "10.228.104.100"
port = 5678
asyncio.get_event_loop().run_until_complete(main_logic(ip, port))
