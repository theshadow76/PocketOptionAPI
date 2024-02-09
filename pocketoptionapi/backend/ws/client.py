import urllib
import websocket
from pocketoptionapi.constants import REGION
import threading
import logging
import ssl

class WebSocketClient:
    def __init__(self, url, pocket_api_instance=None):
        self.url = url
        self.pocket_api_instance = pocket_api_instance
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

        # Create file handler and add it to the logger
        file_handler = logging.FileHandler('pocket.log')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        self.ws = websocket.WebSocketApp(self.url,
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.logger.info("Starting websocket client...")
    def reconnect(self):
        # List of regions to try
        print("Reconecting...")
        self.logger.info("Reconnecting...")
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
        data = message.decode("utf8")
        print(data)
        self.logger.info(f"Recieved a message!: {data}")

        if '"pingInterval":25000,"pingTimeout":20000,"maxPayload":1000000' in data:
            # self.api.send_websocket_request(msg="40")
            self.logger.info("Wup Wup, we are sending the 40 request!")
            ws.send(b'40')

    def on_error(self, ws, error):
        print(error)
        self.logger.error(f"Got a error: {error}")
        self.reconnect()

    def on_close(self, ws, close_status_code, close_msg):
        print("### closed ###")
        self.logger.warning(f"Connection closed, conections status_code: {close_status_code} and the message is: {close_msg}")
        self.reconnect()

    def on_open(self, ws):
        print("Opened connection")
        self.logger.info("Opened!")
        if self.pocket_api_instance:
            self.pocket_api_instance.connected_event.set()
        self.ws.run_forever() # test

    def run(self):
        self.ws.run_forever()  # Use dispatcher for automatic reconnection
