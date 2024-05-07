import random
import time
import dotenv
import asyncio
from pocketoptionapi.stable_api import PocketOption
import os
import time
# dotenv.load_dotenv()
SSID=r"""42["auth",{"session":"a:4:{s:10:\"session_id\";s:32:\"0641660deb66bacfe493ee595ad5bcd6\";s:10:\"ip_address\";s:12:\"190.162.4.33\";s:10:\"user_agent\";s:120:\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 OPR/107.\";s:13:\"last_activity\";i:1715088712;}bf42446033b557288d0399ac1527842c","isDemo":0,"uid":27658142,"platform":2}]"""
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
        exp_time = int(time.time()) + 5000
        api.buy(amount=12, ACTIVES="EURUSD", ACTION="call", expirations=exp_time)
        time.sleep(5)
        try:
            asyncio.run(api.reconect())
        except:
            pass
        if api.check_connect():
           print(api.get_balance())
           api.buy(amount=12, ACTIVES="EURUSD", ACTION="call", expirations=exp_time)
           break  # Exit loop if connected
    else:
        print("Failed to connect after max retries")

if __name__ == '__main__':
    main()