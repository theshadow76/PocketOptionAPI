import json
import logging
import websocket
import pocketoptionapi.constants as OP_code
import pocketoptionapi.global_value as global_value
import collections

import time
class WebsocketClient(object):

    def __init__(self, api):

        self.api = api

        self.wss = websocket.WebSocketApp(
            self.api.wss_url, on_message=self.on_message,
            on_error=self.on_error, on_close=self.on_close,
            on_open=self.on_open,header=self.api.header)

    def on_message(self, wss,raw_message):

        global_value.ssl_Mutex[self.api.object_id].acquire()
        logger = logging.getLogger(__name__)
        logger.debug(raw_message)
        #raw_message = json.loads(str(raw_message))
        if global_value.client_callback != None:
            global_value.client_callback(raw_message)
        #特殊處理
        if raw_message=="""451-["updateAssets",{"_placeholder":true,"num":0}]""":
            
            self.api.async_name=raw_message
             
        elif raw_message=="""451-["updateStream",{"_placeholder":true,"num":0}]""":
            self.api.async_name=raw_message
        elif raw_message=="""451-["successupdateBalance",{"_placeholder":true,"num":0}]""":
            self.api.async_name=raw_message    
        elif raw_message=="2":
            self.api.send_websocket_request("""3""",False)
        elif self.api.async_name=="""451-["updateAssets",{"_placeholder":true,"num":0}]""":
            
            self.api.async_name=""
           
            ok_json=json.loads(raw_message.decode("utf-8"))
            self.api.updateAssets_data=ok_json
        elif self.api.async_name=="""451-["successupdateBalance",{"_placeholder":true,"num":0}]""":
            
            self.api.async_name=""
           
            ok_json=json.loads(raw_message.decode("utf-8"))
            
            if ok_json["isDemo"]==0:
                global_value.real_balance[id(wss)]=ok_json["balance"]
            elif ok_json["isDemo"]==1:
                global_value.practice_balance[id(wss)]=ok_json["balance"]

            
        elif self.api.async_name=="""451-["updateStream",{"_placeholder":true,"num":0}]""":
            self.api.async_name=""
            ok_json=json.loads(raw_message.decode("utf8"))
            ans={}
            ans["time"]=ok_json[0][1]
            ans["price"]=ok_json[0][2]
            
            self.api.realtime_price[ok_json[0][0]].append(ans)
            
            
 


        if isinstance(raw_message,str):
            if  "pingTimeout" in raw_message and global_value.check_auth_finish[id(wss)]==False:

                logger.debug("40")
                wss.send("40")

                
                global_value.auth_send_count[self.api.object_id]=global_value.auth_send_count[self.api.object_id]+1
            elif "40" in raw_message and global_value.check_auth_finish[id(wss)]==False:
                logger.debug(global_value.SSID[self.api.object_id])
                wss.send(global_value.SSID[self.api.object_id])
                pass
            

            if "successauth" in raw_message:
                 
                global_value.check_websocket_if_connect[id(wss)] = 1
                global_value.check_auth_finish[id(wss)]=True
                pass

         
        try:
            
            ok_json=json.loads(raw_message.decode("utf-8"))
            
            

            """
            b'\x04[["AUDCAD_otc",1625299325.048,0.87461]]'
            """

            if "index" in ok_json:
                self.api.getcandle_data[ok_json["index"]]=ok_json
            
            if "requestId" in ok_json:
                self.api.request_data[str(ok_json["requestId"])]=ok_json
            if "ticket" in ok_json and "amount" in ok_json:
                self.api.check_win_refund_data[ok_json["ticket"]]=ok_json
            
            try:
                for info in ok_json:
                    if "id" in info and "profit" in info:
                        self.api.check_win_close_data[info["id"]]=info
            except:
                pass

        except:
            pass
        global_value.ssl_Mutex[self.api.object_id].release()
    @staticmethod
    def on_error(wss, error):
        """Method to process websocket errors."""
        logger = logging.getLogger(__name__)
        logger.error(error)
        global_value.websocket_error_reason[id(wss)] = str(error)
        global_value.check_websocket_if_error[id(wss)] = True

    @staticmethod
    def on_open(wss):
        """Method to process websocket open."""
        logger = logging.getLogger(__name__)
        logger.debug("Websocket client connected.")
        
         
         
    @staticmethod
    def on_close(wss,close_status_code,close_msg):
        """Method to process websocket close."""
        logger = logging.getLogger(__name__)
        logger.debug("Websocket connection closed.")
        global_value.check_websocket_if_connect[id(wss)] = 0
