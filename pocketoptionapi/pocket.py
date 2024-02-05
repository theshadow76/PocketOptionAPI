# Made by © Vigo Walker
from pocketoptionapi.backend.ws.client import WebSocketClient
import threading
import ssl
import decimal
import pause
import json
import urllib
import websocket
import logging

class PocketOptionApi:
    def __init__(self, token) -> None:
        self.ws_url = "wss://api-fin.po.market/socket.io/?EIO=4&transport=websocket"
        self.token = token
        self.connected_event = threading.Event()
        self.client = WebSocketClient(self.ws_url)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

        self.websocket_client = WebSocketClient(self.ws_url, pocket_api_instance=self)

        # Create file handler and add it to the logger
        file_handler = logging.FileHandler('pocket.log')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        self.logger.info(f"initialiting Pocket API with token: {token}")

        self.ping_thread = threading.Thread(target=self.auto_ping)  # Create a new thread for auto_ping
        self.ping_thread.daemon = True  # Set the thread as a daemon so it will terminate when the main program terminates
        self.ping_thread.start()  # Start the auto_ping thread

        self.websocket_client.ws.run_forever()
    def auto_ping(self):
        self.logger.info("Starting auto ping thread")

        while True:
            pause.seconds(5)  # Assuming that you've imported 'pause'
            try:
                if self.websocket_client.ws.sock and self.websocket_client.ws.sock.connected:  # Check if socket is connected
                    self.ping()
                else:
                    self.logger.warning("WebSocket is not connected. Attempting to reconnect.")
                    # Attempt reconnection
                    if self.connect():
                        self.logger.info("Successfully reconnected.")
                    else:
                        self.logger.warning("Reconnection attempt failed.")
                    try:
                        self.ping()
                        self.logger.info("Sent ping reuqests successfully!")
                    except Exception as e:
                        self.logger.error(f"A error ocured trying to send ping: {e}")
            except Exception as e:  # Catch exceptions and log them
                self.logger.error(f"An error occurred while sending ping or attempting to reconnect: {e}")
                try:
                    self.logger.warning("Trying again...")
                    v1 = self.connect()
                    if v1:
                        self.logger.info("Conection completed!, sending ping...")
                        self.ping()
                    else:
                        self.logger.error("Connection was not established")
                except Exception as e:
                    self.logger.error(f"A error ocured when trying again: {e}")

            pause.seconds(5)  # Assuming that you've imported 'pause'

    def connect(self):
        self.logger.info("Attempting to connect...")
        try:
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

            self.logger.info("Connection successful.")

            pause.seconds(5)
            self.send_websocket_request(msg="40")
        except Exception as e:
            print(f"Going for exception.... error: {e}")
            self.logger.error(f"Connection failed with exception: {e}")

            self.websocket_client.reconnect()
    def send_websocket_request(self, msg):
        """Send websocket request to PocketOption server.
        :param dict msg: The websocket request msg.
        """
        self.logger.info(f"Sending websocket request: {msg}")
        def default(obj):
            if isinstance(obj, decimal.Decimal):
                return str(obj)
            raise TypeError

        data = json.dumps(msg, default=default)

        try:
            self.logger.info("Request sent successfully.")
            self.websocket_client.ws.send(bytearray(urllib.parse.quote(data).encode('utf-8')), opcode=websocket.ABNF.OPCODE_BINARY)
            pause.seconds(5)
            return True
        except Exception as e:
            self.logger.error(f"Failed to send request with exception: {e}")
            # Consider adding any necessary exception handling code here
            try:
                self.websocket_client.reconnect()
                self.websocket_client.ws.send(bytearray(urllib.parse.quote(data).encode('utf-8')), opcode=websocket.ABNF.OPCODE_BINARY)
                pause.seconds(5)
            except Exception as e:
                self.logger.warning(f"Was not able to reconnect: {e}")
                pause.seconds(5)

    @property
    def ping(self):
        self.send_websocket_request(msg="3")
        self.logger.info("Sent a ping request")
        return True
