import random
import time

from pocketoptionapi.stable_api import PocketOption

ssid = (r'')
api = PocketOption(ssid)


def direction():
    # Selecciona aleatoriamente entre 'call' y 'put'
    return random.choice(['call', 'put'])


if __name__ == "__main__":
    api.connect()
    time.sleep(2)

    print(api.check_connect(), "check connect")

    data_candles = api.get_candles("AUDNZD_otc", 60, time.time(), count_request=1)

    data, diff = api.process_candle(data_candles, 60)
    print(data)
    print(diff)
    data.to_csv('datos_AUDNZD_otc_test.csv', index=False)
    while api.check_connect():
        print(api.get_server_timestamp(), "server datetime")
        time.sleep(1)

    # Cierra la conexión con la API
