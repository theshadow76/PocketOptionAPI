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
        self.header = "Origin: https://google.com"
        self.ws = websocket.WebSocketApp(self.url,
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close,
                                         header=[self.header])
        self.logger.info("Starting websocket client...")
        try:
            self.ws.send("40")
            data = r"""42["auth",{"session":"a:4:{s:10:\"session_id\";s:32:\"d8fa39dd2f2f58e34e8640fd61f054c2\";s:10:\"ip_address\";s:10:\"90.36.9.15\";s:10:\"user_agent\";s:120:\"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 OP\";s:13:\"last_activity\";i:1707062743;}6b3f96969615d299c7bbbbb5b2a5ddcd","isDemo":1,"uid":27658142,"platform":1}]"""
            self.ws.send(data)
        except:
            self.reconnect()
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
                    on_open=self.on_open,
                    header=[self.header]
                )

                self.wss.run_forever()

                print("Reconected!")
                break  # Break the loop if connection is successful
            except Exception as e:
                print(f"Was not able to connect to: {region} and the error is: {e}")
                self.logger.error(f"Was not able to connect to: {region} and the error is: {e}")
                continue  # Try the next region

    def on_message(self, ws, message):
        print(f"Message: {message}")
        self.logger.info(f"Recieved a message!: {message}")

        if str(message).startswith('0{"sid":'):
            ws.send("40")
        if str(message).startswith('40{"sid"'):
            data = r'42["auth",{"session":"a:4:{s:10:\"session_id\";s:32:\"da7a5a82c8f6c35a87b2ee31d4f5b3b4\";s:10:\"ip_address\";s:10:\"90.36.9.15\";s:10:\"user_agent\";s:120:\"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 OP\";s:13:\"last_activity\";i:1707667599;}3a0058a58a6df5e7b49f652f8e4f8249","isDemo":0,"uid":27658142,"platform":1}]'
            print(f"Sent the auth messaage!: {data}")
            ws.send(data)
        

    def on_error(self, ws, error):
        print(error)
        self.logger.error(f"Got a error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("### closed ###")
        self.logger.warning(f"Connection closed, conections status_code: {close_status_code} and the message is: {close_msg}")

    def on_open(self, ws):
        print("Opened connection")
        self.logger.info("Opened!")

    def run(self):
        self.ws.run_forever()  # Use dispatcher for automatic reconnection
