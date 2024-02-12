import websocket
import logging

class WebSocketClientChat:
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

    def on_message(self, ws, message):
        print(f"Message: {message}")
        self.logger.info(f"Recieved a message!: {message}")

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
