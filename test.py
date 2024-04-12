import random
import time
import dotenv
import asyncio
from pocketoptionapi.stable_api import PocketOption
import os
dotenv.load_dotenv()
SSID=(r'42["auth",{"session":"a:4:{s:10:"session_id";s:32:"a1dc009a7f1f0c8267d940d0a036156f";s:10:"ip_address";s:12:"190.162.4.33";s:10:"user_agent";s:120:"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OP";s:13:"last_activity";i:1709914958;}793884e7bccc89ec798c06ef1279fcf2","isDemo":1,"uid":27658142,"platform":1}]')
api = PocketOption(SSID)
print(SSID)

def direction():
    # Selecciona aleatoriamente entre 'call' y 'put'
    return random.choice(['call', 'put'])

def main():
    api.connect()

    max_retries = 5
    for _ in range(max_retries):
        print(api.get_balance())
        time.sleep(5)
        try:
            asyncio.run(api.reconect())
        except:
            pass
        if api.check_connect(): 
           print(api.get_balance())
           break  # Exit loop if connected
    else:
        print("Failed to connect after max retries")

if __name__ == '__main__':
    main()