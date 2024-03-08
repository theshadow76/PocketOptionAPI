# Client.py made by © Vigo Walker

import websockets
import anyio
from rich.pretty import pprint as print
import json

class WebSocketClient:
    def __init__(self, session) -> None:
        self.SESSION = session
    async def websocket_client(self, url, pro):
        while True:
            try:
                async with websockets.connect(
                    url,
                    extra_headers={
                        # "Origin": "https://pocket-link19.co",
                        "Origin": "https://po.trade/"
                    },
                ) as websocket:
                    async for message in websocket:
                        await pro(message, websocket, url)
            except KeyboardInterrupt:
                exit()
            except Exception as e:
                print(e)
                print("Connection lost... reconnecting")
                await anyio.sleep(5)
        return True


    async def pro(self, message, websocket, url):
        # if byte data
        if type(message) == type(b""):
            # cut 100 first symbols of byte date to prevent spam
            print(str(message)[:100])
            return
        else:
            print(message)

        # Code to make order
        # data = r'42["openOrder",{"asset":"#AXP_otc","amount":1,"action":"call","isDemo":1,"requestId":14680035,"optionType":100,"time":20}]'
        # await websocket.send(data)

        if message.startswith('0{"sid":"'):
            print(f"{url.split('/')[2]} got 0 sid send 40 ")
            await websocket.send("40")
        elif message == "2":
            # ping-pong thing
            print(f"{url.split('/')[2]} got 2 send 3")
            await websocket.send("3")

        if message.startswith('40{"sid":"'):
            print(f"{url.split('/')[2]} got 40 sid send session")
            await websocket.send(self.SESSION)
            print("message sent! We are logged in!!!")


    async def main(self):
        url = "wss://api-l.po.market/socket.io/?EIO=4&transport=websocket"
        await self.websocket_client(url, self.pro)
