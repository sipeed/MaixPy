import asyncio
import websockets
import functools

async def recv_msg(websocket):
    print("new client connected, recv_msg start")
    while True:
        try:
            recv_text = await websocket.recv()
        except Exception as e:
            print("receive failed")
            break
        print("received:", recv_text)
        response_text = f"ack for msg: {recv_text}"
        await websocket.send(response_text)
    print("recv_msg end")

async def main_logic(websocket, path, other_param):
    await recv_msg(websocket)

ip = "0.0.0.0"
port = 5678
start_server = websockets.serve(functools.partial(main_logic, other_param="test_value"), ip, port)
print("start server")
asyncio.get_event_loop().run_until_complete(start_server)
print("start server loop")
asyncio.get_event_loop().run_forever()

