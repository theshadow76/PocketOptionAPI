from pocketoptionapi.backend.ws.client import WebSocketClient
import anyio

data = r'42["auth",{"session":"a:4:{s:10:\"session_id\";s:32:\"d8fa39dd2f2f58e34e8640fd61f054c2\";s:10:\"ip_address\";s:14:\"90.36.9.15\";s:10:\"user_agent\";s:101:\"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36\";s:13:\"last_activity\";i:1707850603;}9f383935faff5a86bc1658bbde8c61e7","isDemo":1,"uid":27658142,"platform":3}]'

async def main():
    url = "wss://api-l.po.market/socket.io/?EIO=4&transport=websocket"
    wb = WebSocketClient(session=data)
    await wb.websocket_client(url=url, pro=wb.pro)

if __name__ == '__main__':
    anyio.run(main)