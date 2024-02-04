import websocket
from pocketoptionapi.constants import REGION
import threading
import ssl

class WebSocketClient:
    def __init__(self, url):
        self.url = url
        self.ws = websocket.WebSocketApp(self.url,
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
    def reconnect(self):
        # List of regions to try
        print("Reconecting...")
        REG = REGION()
        regions = REG.get_regions()

        for region in regions:
            try:
                self.wss = websocket.WebSocketApp(
                    region,
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=self.on_close,
                    on_open=self.on_open
                )
                # Here you might want to establish the connection
                # Depending on how your WebSocketApp is set up, you might need to start a new thread or use `run_forever`
                self.websocket_thread = threading.Thread(target=self.wss.run_forever, kwargs={
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
                print("Reconected!")
                break  # Break the loop if connection is successful
            except Exception as e:
                print(f"Was not able to connect to: {region} and the error is: {e}")
                continue  # Try the next region

    def on_message(self, ws, message):
        print(message)

    def on_error(self, ws, error):
        print(error)
        self.reconnect()

    def on_close(self, ws, close_status_code, close_msg):
        print("### closed ###")
        self.reconnect()

    def on_open(self, ws):
        print("Opened connection")

    def run(self):
        self.ws.run_forever()  # Use dispatcher for automatic reconnection
