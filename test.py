import random
import time
import dotenv
from pocketoptionapi.stable_api import PocketOption
import os
dotenv.load_dotenv()
ssid = os.getenv("SSID")
api = PocketOption(ssid)
print(ssid)

def direction():
    # Selecciona aleatoriamente entre 'call' y 'put'
    return random.choice(['call', 'put'])

if __name__ == "__main__":
    api.connect()
    time.sleep(2)
