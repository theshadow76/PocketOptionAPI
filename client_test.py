import websockets
import anyio
from rich.pretty import pprint as print
import json
from pocketoptionapi.constants import REGION

SESSION = r'42["auth",{"session":"a:4:{s:10:\"session_id\";s:32:\"a1dc009a7f1f0c8267d940d0a036156f\";s:10:\"ip_address\";s:12:\"190.162.4.33\";s:10:\"user_agent\";s:120:\"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OP\";s:13:\"last_activity\";i:1709914958;}793884e7bccc89ec798c06ef1279fcf2","isDemo":0,"uid":27658142,"platform":1}]'


async def websocket_client(url, pro):
    for i in REGION.get_regions(REGION):
        print(f"Trying {i}...")
        try:
            async with websockets.connect(
                i, #teoria de los issues
                extra_headers={
                    #"Origin": "https://pocket-link19.co",
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
            # await anyio.sleep(5)
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