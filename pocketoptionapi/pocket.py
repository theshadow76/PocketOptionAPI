# Made by © Vigo Walker
from pocketoptionapi.backend.ws.client import WebSocketClient

class PocketOptionApi:
    def __init__(self, token) -> None:
        self.ws_url = "wss://api-fin.po.market/socket.io/?EIO=4&transport=websocket"
        self.token = token
        self.client = WebSocketClient(self.ws_url)
    def connect(self):
        # Init the websocket
        self.client.run()