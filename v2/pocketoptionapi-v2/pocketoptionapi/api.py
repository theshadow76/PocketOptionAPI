 
import time
import json
import logging
import threading
import requests
import ssl
import atexit
import tempfile
from des import DesKey
import base64
from collections import deque
import sqlite3
from pocketoptionapi.http.login import Login
 
from pocketoptionapi.http.logout import Logout
 
from pocketoptionapi.ws.client import WebsocketClient
from pocketoptionapi.ws.chanels.subscribe import *
from pocketoptionapi.ws.chanels.unsubscribe import *

from pocketoptionapi.ws.chanels.auth import *
from pocketoptionapi.ws.chanels.ping_server import *
from pocketoptionapi.ws.chanels.buy import *
from pocketoptionapi.ws.chanels.candle import *
from pocketoptionapi.ws.chanels.get_balance import *
from pocketoptionapi.ws.chanels.get_asset_data import *

import pocketoptionapi.global_value as global_value

import collections
from collections import defaultdict


 
# InsecureRequestWarning: Unverified HTTPS request is being made.
# Adding certificate verification is strongly advised.
# See: https://urllib3.readthedocs.org/en/latest/security.html
requests.packages.urllib3.disable_warnings()  # pylint: disable=no-member

def nested_dict(n, type):
    if n == 1:
        return defaultdict(type)
    else:
        return defaultdict(lambda: nested_dict(n-1, type))

class pocketoptionapi(object):   
     
    def __init__(self, wss, header=None,proxies=None,set_ssid=None,auto_logout=True,_2FA_TOKEN=None):
         
        self.server_timestamp={}
        self.real_time_canlde=nested_dict(2, dict)
        self.real_time_quote={}
        self.raw_e98={}
        self.request_data={}
        self.buy_data={}
        self.check_win_end={}
        self.check_win_refund_data={}
        self.check_win_close_data={}
        self.sub_uid={}
        self.buy_info={}
        self.header=header
        self.wss_url = wss
        self.websocket_client = None
        self.session = requests.Session()
        self.session.verify = False
        self.session.trust_env = False
        
        self.getcandle_data={}
        self.proxies = proxies
        self._2FA_TOKEN=_2FA_TOKEN
        # is used to determine if a buyOrder was set  or failed. If
        # it is None, there had been no buy order yet or just send.
        # If it is false, the last failed
        # If it is true, the last buy order was successful
        self.buy_successful = None
        self.object_id=None
        self.set_ssid=set_ssid
        self.auto_logout=auto_logout
        self.realtime_price={}
        self.updateAssets_data=None

        self.auto_tmp_session={}
        self.async_name=""

        self.conn = sqlite3.connect(tempfile.gettempdir()+"/.pocketoptionapi")
         
     
        self.c = self.conn.cursor()
        self.c.execute('''create table if not exists session (email  CHAR(100)  PRIMARY KEY ,session  CHAR(200));''')
        self.conn.commit()

        #self._input_session("sdsss","twwt")
         
        
    def _get_session(self,email):
        cursor = self.c.execute("SELECT session from session Where email='"+email+"';") 
        data=cursor.fetchall()
        if len(data)==0:
            return None
        else:   
            return data[0][0]
         

    def _input_session(self,email,session):
        try:
            self.c.execute("INSERT INTO session (email,session) VALUES ('"+email+"','"+session+"' );")
        except:
            self.c.execute("UPDATE session set session = '"+session+"' where email='"+email+"' ")
        self.conn.commit()

    def send_http_request(self, url, method, data=None, params=None, headers=None,cookies=None):  # pylint: disable=too-many-arguments
        
        logger = logging.getLogger(__name__)

        logger.debug(method+": "+url+" headers: "+str(self.session.headers)+" cookies: "+str(self.session.cookies.get_dict()))
        
        
        response = self.session.request(method=method,
                                        url=url,
                                        data=data,
                                        params=params,
                                        headers=headers,
                                        proxies=self.proxies,
                                        cookies=cookies)
        logger.debug(response)
        logger.debug(response.text)
        logger.debug(response.headers)
        logger.debug(response.cookies)
         
        
        return response

    @property
    def websocket(self):
        
        return self.websocket_client.wss

    def send_websocket_request(self,data,no_force_send=True):
        if global_value.check_websocket_if_connect[self.object_id]==1:
            logger = logging.getLogger(__name__)    
            data=data.replace("\\\\","\\")
            data=data.replace("'","\"")
            if no_force_send==False:
                self.websocket.send(data)
            else:
                global_value.ssl_Mutex[self.object_id].acquire()
                self.websocket.send(data)
                global_value.ssl_Mutex[self.object_id].release()
            logger.debug(data)
       
    def init_ansyc_data(self):
        get=[{"t":2,"e":98,"uuid":"KDOJ6MMIERN26ZDIRV7","d":[22,20,21,26]}]

        self.send_websocket_request(get)
    
    def get_server_time(self,req_id:str=""):
        get=[{"t":2,"e":90,"uuid":req_id}]

        self.send_websocket_request(get)
         
         
    @property
    def subscribe_realtime_candle(self):
        
        return changeSymbol(self)

    @property
    def unsubscribe_realtime_candle(self):
        return unsubfor(self)


    @property
    def logout(self):
         
        return Logout(self)
    @property
    def Auth_Mode(self):
        return auth_mode(self)
    @property
    def login(self):
         
        return Login(self)
    @property
    def ping_to_server(self):
        return Ping_To_Server(self)
    @property
    def TWO_FA(self):
        return _2FA(self)
     
    @property
    def Get_Balance(self):
        
        return get_balance(self)
    @property
    def Get_Asset_Data(self):
        
        return get_asset_data(self)
 
    @property
    def ssid(self):
        
        return Ssid(self)
 
    
   
    @property
    def getcandles(self):
        
        return loadHistoryPeriod(self)

   
  
    @property
    def buy(self): 
        return buy_binary(self)

    @property
    def sell_option(self):
        return cancelOrder(self)
 
 
    def set_session(self,cookies,headers):
 
        self.session.headers.update(headers)
         
        self.session.cookies.clear_session_cookies()
        requests.utils.add_dict_to_cookiejar(self.session.cookies, cookies)
    def init_global_value(self,object_id):
        global_value.ssl_Mutex[object_id]=threading.Lock()
        global_value.check_websocket_if_connect[object_id]=None
        # try fix ssl.SSLEOFError: EOF occurred in violation of protocol (_ssl.c:2361)
       
        #if false websocket can sent self.websocket.send(data)
        #else can not sent self.websocket.send(data)
       
        if object_id not in global_value.SSID:
            global_value.SSID[object_id]=self.set_ssid

        global_value.check_websocket_if_error[object_id]=False
        global_value.websocket_error_reason[object_id]=None
        #start account is demo
        global_value.account_mode_isDemo[object_id]=1
        
        global_value.balance_id[object_id]=0
        global_value.check_auth_finish[object_id]=False
        global_value.balance[object_id]=nested_dict(2,dict)
        global_value.req_mutex[object_id]=threading.Lock()
        global_value.req_id[object_id]=1
        global_value.auth_send_count[object_id]=0
        global_value.real_balance[object_id]=None
        global_value.practice_balance[object_id]=None


    def del_init_global_value(self,object_id):
        del global_value.check_websocket_if_connect[object_id] 
        del global_value.SSID[object_id] 
        del global_value.check_websocket_if_error[object_id] 
        del global_value.websocket_error_reason[object_id] 
        del global_value.balance_id[object_id]
        del global_value.req_mutex[object_id] 
        del global_value.req_id[object_id] 
        del global_value.balance[object_id] 
    def start_websocket(self):
        
        self.websocket_client = WebsocketClient(self)
        try:
            self.del_init_global_value(self.object_id)
        except:
            pass
        # update self.object_id
        self.object_id=id(self.websocket_client.wss)
        self.init_global_value(self.object_id)
        
        try:
            import re
            p = '(?:http.*://)?(?P<host>[^:/ ]+).?(?P<port>[0-9]*).*'

            m = re.search(p,self.proxies["http"])
            http_proxy_host=m.group('host') # 'www.abc.com'
            http_proxy_port=m.group('port') # '123'     
        except:
            http_proxy_host=None
            http_proxy_port=None

        self.websocket_thread = threading.Thread(target=self.websocket.run_forever,kwargs={'sslopt': {
                                                 "check_hostname": False, "cert_reqs": ssl.CERT_NONE, "ca_certs": "cacert.pem"},"http_proxy_host":http_proxy_host,"http_proxy_port":http_proxy_port,"suppress_origin":True})  # for fix pyinstall error: cafile, capath and cadata cannot be all omitted
        self.websocket_thread.daemon = True
        self.websocket_thread.start()
         
        start_time=time.time()
        while True:
             
            if global_value.check_websocket_if_error[self.object_id]:
                return False,global_value.websocket_error_reason[self.object_id]
            if global_value.check_websocket_if_connect[self.object_id] == 0 :
                global_value.websocket_error_reason[self.object_id]="Websocket connection closed."
                return False,global_value.websocket_error_reason[self.object_id]
            elif global_value.check_websocket_if_connect[self.object_id] == 1:
                return True,None
            if time.time()-start_time>global_value.wait_connect_sec:
                global_value.websocket_error_reason[self.object_id]="Connect Error"
                return False,global_value.websocket_error_reason[self.object_id]
                
           
             
            pass
    def get_ssid(self):
        response=None
        response = self.login(self.username, self.password,self._2FA_TOKEN)  #  
        if "session" in response.cookies:
            self._input_session(self.username,response.cookies["session"])
        return response
    
    def connect(self):
         
        try:
            self.logout()
        except:
            pass
        if self.auto_logout:
            atexit.register(self.logout)
        
        check_websocket,websocket_reason=self.start_websocket()
        if check_websocket==False:
            return check_websocket,websocket_reason
        #set ssis cookie

        
        return True,None

    def close(self):
        self.websocket.close()
        self.websocket_thread.join()

    def websocket_alive(self):
        return self.websocket_thread.is_alive()

    @property
    def Get_User_Profile_Client(self):
        return Get_user_profile_client(self)
    @property
    def Request_Leaderboard_Userinfo_Deals_Client(self):
        return Request_leaderboard_userinfo_deals_client(self)
    @property
    def Get_Users_Availability(self):
        return Get_users_availability(self)
