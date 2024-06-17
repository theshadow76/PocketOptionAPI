# dev @vigo_walker, github: https://github.com/theshadow76

# python
from pocketoptionapi.api import pocketoptionapi
import pocketoptionapi.constants as OP_code
import pocketoptionapi.country_id as Country
import threading
import time
import logging
import operator
import pocketoptionapi.global_value as global_value
from pocketoptionapi.expiration import get_expiration_time, get_remaning_time
from datetime import datetime, timedelta,timezone
from collections import defaultdict
from collections import deque
import collections
import json
import threading
def nested_dict(n, type):
    if n == 1:
        return defaultdict(type)
    else:
        return defaultdict(lambda: nested_dict(n-1, type))
def ping_server(self):
    
    t = threading.currentThread()
    while getattr(t, "do_run", True):
        if global_value.check_websocket_if_connect[self.api.object_id]==0:
            break
        time.sleep(10)
        self.ping_server_go()
        
        

 
class PocketOption:
    __version__ = "2.2"

    def __init__(self,set_ssid,proxies=None,auto_logout=True,websocket_url=None,wait_connect_sec=2):
        
        self.SESSION_HEADER={"Origin": "https://pocketoption.com","Sec-WebSocket-Version":"13","Connection":"Upgrade","Accept-Encoding:":"gzip, deflate, br","Sec-WebSocket-Extensions":"permessage-deflate; client_max_window_bits","User-Agent":r"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"}
        self.SESSION_COOKIE={}
        self.proxies=proxies
        self.set_ssid=set_ssid
        self.auto_logout=auto_logout
        self._2FA_TOKEN=None
        self.websocket_url=websocket_url
        global_value.wait_connect_sec=wait_connect_sec
 # --------------------------------------------------------------------------
    def logout(self):
        self.api.logout()
    def ping_server_go(self):
        self.api.ping_to_server()
 
    def set_call_back_for_client(self,function):
        global_value.client_callback=function
    def set_session(self,header,cookie):
        self.SESSION_HEADER=header
        self.SESSION_COOKIE=cookie
     
    def get_ssid(self):
        return global_value.SSID[self.api.object_id] 

    def setting_2FA_TOKEN(self,code):
        self._2FA_TOKEN=code
    def TWO_FA(self, token,method=None,code=None):
        r=self.api.TWO_FA(token,method,code)
        return json.loads(r.text)
    def close(self):
        
        self._thread_ping_server.do_run = False
    def connect(self):
         
        try:
            self.api.close()
        except:
            pass
            #logging.error('**warning** self.api.close() fail')
 
        #id-iqoption.com some country only can using this url
        #Iqoption.com
        try:   
            self.set_ssid=global_value.SSID[self.api.object_id]
        except:
            pass
        
        
        if self.websocket_url==None:
            for url in global_value.websocket_url:
                self.api = pocketoptionapi(url,header=self.SESSION_HEADER,proxies=self.proxies,set_ssid=self.set_ssid,auto_logout=self.auto_logout,_2FA_TOKEN=self._2FA_TOKEN)
                c,m=self.api.connect()
                if c:
                    break
                elif m=="""42["NotAuthorized"]""":
                    return False,m
        else:
            self.api = pocketoptionapi(self.websocket_url,header=self.SESSION_HEADER,proxies=self.proxies,set_ssid=self.set_ssid,auto_logout=self.auto_logout,_2FA_TOKEN=self._2FA_TOKEN)
            c,m=self.api.connect()

            if m=="""42["NotAuthorized"]""":
                return False,m

        if c:
            self.change_balance("PRACTICE")
            self._thread_ping_server=threading.Thread(target = ping_server, args = (self,))
            self._thread_ping_server.start()
        return c,m
         
    
    def check_connect(self):
        # True/False
         
        if global_value.check_websocket_if_connect[self.api.object_id] == 0:
            return False
        else:
            return True
        # wait for timestamp getting

# _________________________UPDATE ACTIVES OPCODE_____________________

    def _init_get_raw_balance(self):
        #[{"d":[{"value":3686.24}],"e":52},{"d":[{"value":20.10,"account_id":1250470807}],"e":50}]

        req_id="balance"
        self.api.raw_e98[req_id]=None
        self.api.Get_Balance(req_id)
        
        while self.api.raw_e98[req_id]==None:
            pass
        _tmp=self.api.raw_e98[req_id]
        del self.api.raw_e98[req_id]
        for d in _tmp:
            try:
                if "account_id" in d["d"][0]:
                    global_value.balance[self.api.object_id]["REAL"]["value"]=d["d"][0]["value"]
                    global_value.balance[self.api.object_id]["REAL"]["account_id"]=d["d"][0]["account_id"]
                elif  "value" in  d["d"][0]:
                    global_value.balance[self.api.object_id]["PRACTICE"]["value"]=d["d"][0]["value"]
                    global_value.balance[self.api.object_id]["PRACTICE"]["account_id"]=0
            except:
                pass
            
    
    def get_balance(self):
        if global_value.account_mode_isDemo[self.api.object_id]==0:
            while global_value.real_balance[self.api.object_id]==None:
                pass
            return global_value.real_balance[self.api.object_id]
        elif global_value.account_mode_isDemo[self.api.object_id]==1:
            while global_value.practice_balance[self.api.object_id]==None:
                pass
            return global_value.practice_balance[self.api.object_id]

    def get_asset_data(self):
        req_id=global_value.get_req_id(self.api.object_id)
         
        self.api.raw_e98["e_70"]=None
        self.api.Get_Asset_Data(req_id)
        while self.api.raw_e98["e_70"]==None:
            pass
        _tmp=self.api.raw_e98["e_70"]
        del self.api.raw_e98["e_70"]
        return _tmp
    def change_balance(self, Balance_MODE):
        
         
        if Balance_MODE=="REAL":
            global_value.check_auth_finish[self.api.object_id]=False
            while global_value.check_auth_finish[self.api.object_id]==False:
                self.api.Auth_Mode(Balance_MODE)
                time.sleep(0.5)
            global_value.account_mode_isDemo[self.api.object_id]=0
        elif Balance_MODE=="PRACTICE":
            global_value.check_auth_finish[self.api.object_id]=False
            while global_value.check_auth_finish[self.api.object_id]==False:
                self.api.Auth_Mode(Balance_MODE)
                time.sleep(0.5)
            global_value.account_mode_isDemo[self.api.object_id]=1
        else:
            logging.error('**warning** change_balance() need input "REAL"/"PRACTICE" ')
 
         
         
# ________________________________________________________________________
# _______________________        CANDLE      _____________________________
# ________________________self.api.getcandles() wss________________________

    def get_candle(self, Asset, _from, timeframe,request_id=""):
        self.api.getcandles(Asset, _from, timeframe,request_id)
        pass
#######################################################
# ______________________________________________________
# _____________________REAL TIME CANDLE_________________
# ______________________________________________________
#######################################################

    def get_payment(self):
        raw_asset=self.get_raw_asset()
        ans=nested_dict(2,dict)
        for i in raw_asset:
            asset_name=i[1]
            ans[asset_name]["payment"]=i[5]
            ans[asset_name]["open"]=i[14]

        return ans
      
    def get_raw_asset(self):
        while self.api.updateAssets_data==None:
            pass
        return self.api.updateAssets_data
    def get_all_asset_name(self):
        all_asset=self.get_raw_asset()
        ans=[]
        for i in all_asset:
            ans.append(i[1])
        return ans

    def check_asset_open(self,asset):
        all_asset=self.get_raw_asset()
        for i in all_asset:
            if i[1]==asset:
                if True in i:
                    return True
                else:
                    return False
        
    def start_candles_stream(self,asset,size):
        #the list of the size
        self.api.subscribe_realtime_candle(asset,size)

    def stop_candles_stream(self, asset):
        self.api.unsubscribe_realtime_candle(asset)
        
    def get_realtime_candles(self, asset):
        while True:
            if asset in self.api.realtime_price:
                if len(self.api.realtime_price[asset])>0:
                    return self.api.realtime_price[asset]
         
         
    def buy(self,asset,amount,dir,duration):
        # the min duration is 30
        #if duration<30:
        #    duration=30
        req_id=global_value.get_req_id(self.api.object_id)
        self.api.request_data[req_id]=None
        self.api.buy(asset,amount,dir,duration,req_id)
        while self.api.request_data[req_id]==None:
            pass
        _tmp=self.api.request_data[req_id]
        del self.api.request_data[req_id]
        if "id" in _tmp:
            self.api.buy_info[_tmp["id"]]=_tmp
        return _tmp

    def sell_option(self,id):
        # the min duration is 30
        self.api.sell_option(id)
         
    def get_candle(self,asset,time,offset,period):
        req_id=global_value.get_req_id(self.api.object_id)
        self.api.getcandle_data[req_id]=None
        self.api.getcandles(asset,time,offset,period,req_id)
        while self.api.getcandle_data[req_id]==None:
            pass
        return self.api.getcandle_data[req_id]
        

       
    def check_win(self,ticket,polling=1):
        while True:  
            if ticket  in self.api.check_win_refund_data:
                return self.api.check_win_refund_data[ticket]["amount"]-self.api.buy_info[ticket]
            elif ticket  in self.api.check_win_close_data:
                 
                  
                if self.api.check_win_close_data[ticket]["closePrice"]!=0:
                    return self.api.check_win_close_data[ticket]["profit"]

            time.sleep(polling)
        
         


    def get_server_time(self):
        req_id=global_value.get_req_id(self.api.object_id)
        self.api.server_timestamp[req_id]=None
        self.api.get_server_time(req_id)
        while self.api.server_timestamp[req_id]==None:
            pass
        _tmp=self.api.server_timestamp[req_id]
        del self.api.server_timestamp[req_id]
        return _tmp
         
