import websockets
import anyio
from rich.pretty import pprint as print
import json

SESSION = r'42["auth",{"session":"a:4:{s:10:\"session_id\";s:32:\"da7a5a82c8f6c35a87b2ee31d4f5b3b4\";s:10:\"ip_address\";s:10:\"90.36.9.15\";s:10:\"user_agent\";s:120:\"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 OP\";s:13:\"last_activity\";i:1707667599;}3a0058a58a6df5e7b49f652f8e4f8249","isDemo":1,"uid":27658142,"platform":1}]'


async def websocket_client(url, pro):
    while True:
        try:
            async with websockets.connect(
                url,
                extra_headers={
                    "Origin": "https://pocket-link19.co",
                    # "Origin": "https://po.trade/"
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


async def pro(message, websocket, url):
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
        await websocket.send(SESSION)
        print("message sent! We are logged in!!!")


async def main():
    url = "wss://api-l.po.market/socket.io/?EIO=4&transport=websocket"
    await websocket_client(url, pro)


if __name__ == "__main__":
    anyio.run(main)