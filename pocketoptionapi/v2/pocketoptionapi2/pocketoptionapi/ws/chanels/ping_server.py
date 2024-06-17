from pocketoptionapi.ws.chanels.base import Base
import pocketoptionapi.constants as OP_code
import pocketoptionapi.global_value as global_value
import json
class Ping_To_Server(Base):
    def __call__(self):
        self.send_websocket_request("""42["ps"]""")
         
 