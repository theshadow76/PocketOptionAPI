import random
import time

from pocketoptionapi.stable_api import PocketOption
import logging
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(message)s')
ssid = (r'42["auth",{"session":"vtftn12e6f5f5008moitsd6skl","isDemo":1,"uid":27658142,"platform":1}]')
api = PocketOption(ssid)


if __name__ == "__main__":
    api.connect()
    time.sleep(5)

    print(api.check_connect(), "check connect")

    print(api.get_balance())
