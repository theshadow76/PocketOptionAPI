from pocketoptionapi.ws.chanels.base import Base
import datetime
import pocketoptionapi.constants as OP_code
class Subscribe(Base): 
    def __call__(self,asset,timeframe,req_id):
       #{"name":"subscribeMessage","msg":{"name":"candle-generated","params":{"routingFilters":{"active_id":1,"size":1}}}}
        #data="""[{"t":2,"e":4,"uuid":"gg","d":[{"p":"EURUSD","tf":60}]}]"""
         
        data=[{"t":2,"e":4,"uuid":req_id,"d":[{"p":asset,"tf":timeframe}]}]
        self.send_websocket_request(data)
 