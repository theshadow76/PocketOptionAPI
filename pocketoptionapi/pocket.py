# Made by © Vigo Walker
from pocketoptionapi.backend.ws.client import WebSocketClient
import threading
import ssl
import decimal
import pause
import json
import urllib
import websocket

class PocketOptionApi:
    def __init__(self, token) -> None:
        self.ws_url = "wss://api-fin.po.market/socket.io/?EIO=4&transport=websocket"
        self.token = token
        self.client = WebSocketClient(self.ws_url)
    def connect(self, msg):
        self.websocket_client = WebSocketClient(self.ws_url)

        self.websocket_thread = threading.Thread(target=self.websocket_client.ws.run_forever, kwargs={
            'sslopt': {
                "check_hostname": False,
                "cert_reqs": ssl.CERT_NONE,
                "ca_certs": "cacert.pem"
            },
            "ping_interval": 0,
            'skip_utf8_validation': True,
            "origin": "https://pocketoption.com",
            # "http_proxy_host": '127.0.0.1', "http_proxy_port": 8890
        })

        self.websocket_thread.daemon = True
        self.websocket_thread.start()

        self.send_websocket_request(msg=msg)
    def send_websocket_request(self, msg):
        """Send websocket request to PocketOption server.
        :param dict msg: The websocket request msg.
        """
        def default(obj):
            if isinstance(obj, decimal.Decimal):
                return str(obj)
            raise TypeError

        data = json.dumps(msg, default=default)

        self.websocket_client.ws.send(bytearray(urllib.parse.quote(data).encode('utf-8')), opcode=websocket.ABNF.OPCODE_BINARY)
        pause.seconds(5)
        return True
