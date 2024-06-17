

"""
42["loadHistoryPeriod",{"asset":"USDCAD","index":162513874160,"time":1625138122.445,"offset":1000,"period":5}]
"""
 
 
import collections
from pocketoptionapi.ws.chanels.base import Base
import pocketoptionapi.constants as OP_code
import pocketoptionapi.global_value as global_value
import json
 
 
class loadHistoryPeriod(Base):
    def __call__(self,asset,time,offset,period,index):
        data=["loadHistoryPeriod",{"asset":asset,"index":index,"time":time,"offset":offset,"period":period}]
        self.send_websocket_request("42"+str(data))
 
 
"""
42["changeSymbol",{"asset":"USDCAD","prevAsset":"USDCAD","reason":2,"otherData":{},"period":5}]
"""

 
class changeSymbol(Base):
    def __call__(self,asset,size):
        self.api.realtime_price[asset]=collections.deque([],size)
        data=["changeSymbol",{"asset":asset,"prevAsset":asset,"reason":2,"otherData":{},"period":0}]
        self.send_websocket_request("42"+str(data))
 
 
"""
42["unsubfor","EURRUB_otc"]
"""

class unsubfor(Base):
    def __call__(self,asset):
        data=["subfor",asset]
        self.send_websocket_request("42"+str(data))
 
 