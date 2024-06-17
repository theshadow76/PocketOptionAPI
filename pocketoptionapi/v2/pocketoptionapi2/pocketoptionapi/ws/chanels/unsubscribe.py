from pocketoptionapi.ws.chanels.base import Base
import datetime
import pocketoptionapi.constants as OP_code
class Unsubscribe(Base): 
    def __call__(self,sub_uid,req_id=""):
        data=[{"t":2,"e":5,"uuid":req_id,"d":[{"sub_uid":sub_uid}]}]
 
        self.send_websocket_request(data)
 