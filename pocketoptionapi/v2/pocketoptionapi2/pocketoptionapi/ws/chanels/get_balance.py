from pocketoptionapi.ws.chanels.base import Base
import datetime
import pocketoptionapi.constants as OP_code
class get_balance(Base):
    def __call__(self,req_id):
        data=[{"t":2,"e":98,"uuid":req_id,"d":[52,50]}]
        self.send_websocket_request(data)