 
check_websocket_if_connect={}#None
# try fix ssl.SSLEOFError: EOF occurred in violation of protocol (_ssl.c:2361)
ssl_Mutex={}

#
 
#if false websocket can sent self.websocket.send(data)
#else can not sent self.websocket.send(data)



SSID={}#None

check_websocket_if_error={}#False
websocket_error_reason={}#None

balance_id={}#None
account_mode_isDemo={}#practice is 1, real is 0 (int)
check_auth_finish={}
balance={}

real_balance={}
practice_balance={}

client_callback=None
auth_send_count={}
req_mutex={}#True or object_id
req_id={}
wait_connect_sec=2
def get_req_id(object_id):
    req_mutex[object_id].acquire()
    get_req_id=req_id[object_id]
    req_id[object_id]=req_id[object_id]+1
    req_mutex[object_id].release()

    return str(get_req_id)

websocket_url=[
     
    "wss://api-hk.po.market/socket.io/?EIO=4&transport=websocket",
    "wss://api-fr.po.market/socket.io/?EIO=4&transport=websocket",
    "wss://api-sg2.po.market/socket.io/?EIO=4&transport=websocket",
    "wss://api-in.po.market/socket.io/?EIO=4&transport=websocket",
    "wss://api-in2.po.market/socket.io/?EIO=4&transport=websocket",
    
    "wss://api-msk.po.market/socket.io/?EIO=4&transport=websocket",
    "wss://api-fin.po.market/socket.io/?EIO=4&transport=websocket",
    "wss://api-l.po.market/socket.io/?EIO=4&transport=websocket",
    "wss://api-c.po.market/socket.io/?EIO=4&transport=websocket",
    "wss://api-sc.po.market/socket.io/?EIO=4&transport=websocket",
    "wss://api-asia2.po.market/socket.io/?EIO=4&transport=websocket",
    "wss://api-us2.po.market/socket.io/?EIO=4&transport=websocket",
    "wss://api-us3.po.market/socket.io/?EIO=4&transport=websocket",
    "wss://api-us4.po.market/socket.io/?EIO=4&transport=websocket",
    "wss://api-latina2.po.market/socket.io/?EIO=4&transport=websocket",
    "wss://api-asia.po.market/socket.io/?EIO=4&transport=websocket"
     ]