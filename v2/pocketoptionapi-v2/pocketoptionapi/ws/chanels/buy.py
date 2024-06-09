 
 
from pocketoptionapi.ws.chanels.base import Base
import pocketoptionapi.constants as OP_code
import pocketoptionapi.global_value as global_value
import json
class buy_binary(Base):
    def __call__(self,asset,amount,dir,duration,req_id):
        session=global_value.SSID[self.api.object_id]
        data=[]
        data.append("openOrder")
        openorder={}
        openorder["session"]=json.loads(session[2:])[1]["session"].replace("\"","\\\"")
        openorder["asset"]=asset
        openorder["amount"]=amount
        openorder["action"]=dir
        openorder["requestId"]=req_id
        openorder["isDemo"]=global_value.account_mode_isDemo[self.api.object_id]
        openorder["time"]=duration#sec
        openorder["optionType"]=100
        data.append(openorder)
         
        self.send_websocket_request("42"+str(data))

class cancelOrder(Base):
    def __call__(self,ticket):
        data=["cancelOrder",{"ticket":str(ticket)}]
        self.send_websocket_request("42"+str(data))
 