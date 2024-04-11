# This is a sample Python script.
import asyncio
import threading

from tzlocal import get_localzone

from pocketoptionapi.api import PocketOptionAPI
import pocketoptionapi.constants as OP_code
# import pocketoptionapi.country_id as Country
# import threading
import time
import logging
import operator
import pocketoptionapi.global_value as global_value
from collections import defaultdict
from collections import deque
# from pocketoptionapi.expiration import get_expiration_time, get_remaning_time
import pandas as pd
from pocketoptionapi.ws.chanels.get_balances import *

# Obtener la zona horaria local del sistema como una cadena en el formato IANA
local_zone_name = get_localzone()


def nested_dict(n, type):
    if n == 1:
        return defaultdict(type)
    else:
        return defaultdict(lambda: nested_dict(n - 1, type))


def get_balance():
    # balances_raw = self.get_balances()
    return global_value.balance


class PocketOption:
    __version__ = "6.8.9.1"

    def __init__(self, ssid):
        self.size = [1, 5, 10, 15, 30, 60, 120, 300, 600, 900, 1800,
                     3600, 7200, 14400, 28800, 43200, 86400, 604800, 2592000]
        global_value.SSID = ssid
        self.suspend = 0.5
        self.thread = None
        self.subscribe_candle = []
        self.subscribe_candle_all_size = []
        self.subscribe_mood = []
        # for digit
        self.get_digital_spot_profit_after_sale_data = nested_dict(2, int)
        self.get_realtime_strike_list_temp_data = {}
        self.get_realtime_strike_list_temp_expiration = 0
        self.SESSION_HEADER = {
            "User-Agent": r"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          r"Chrome/66.0.3359.139 Safari/537.36"}
        self.SESSION_COOKIE = {}
        self.api = PocketOptionAPI()
        self.loop = asyncio.get_event_loop()

        #

        # --start
        # self.connect()
        # this auto function delay too long

    # --------------------------------------------------------------------------

    def get_server_timestamp(self):
        return self.api.timesync.server_timestamp

    def get_server_datetime(self):
        return self.api.timesync.server_datetime

    def set_session(self, header, cookie):
        self.SESSION_HEADER = header
        self.SESSION_COOKIE = cookie

    def get_async_order(self, buy_order_id):
        # name': 'position-changed', 'microserviceName': "portfolio"/"digital-options"
        if self.api.order_async["deals"][0]["id"] == buy_order_id:
            return self.api.order_async["deals"][0]
        else:
            return None

    def get_async_order_id(self, buy_order_id):
        return self.api.order_async["deals"][0][buy_order_id]

    def start_async(self):
        asyncio.run(self.api.connect())

    def connect(self):
        """
        Método síncrono para establecer la conexión.
        Utiliza internamente el bucle de eventos de asyncio para ejecutar la coroutine de conexión.
        """
        try:
            # Iniciar el hilo que manejará la conexión WebSocket
            websocket_thread = threading.Thread(target=self.api.connect, daemon=True)
            websocket_thread.start()

        except Exception as e:
            print(f"Error al conectar: {e}")
            return False
        return True

    @staticmethod
    def check_connect():
        # True/False
        if global_value.websocket_is_connected == 0:
            return False
        elif global_value.websocket_is_connected is None:
            return False
        else:
            return True

        # wait for timestamp getting

    # self.update_ACTIVES_OPCODE()
    def get_balance(self):
        self.api.get_balances()
        return {
            "balance_id" : global_value.balance_id,
            "balance" : global_value.balance,
            "balance_type" : global_value.balance_type
        }

    def buy(self, amount, ACTIVES, ACTION, expirations):
        self.api.buy_multi_option = {}
        self.api.buy_successful = None
        req_id = "buy"
        try:
            self.api.buy_multi_option[req_id]["id"] = None
        except:
            pass
        global_value.order_data = None
        global_value.result = None
        self.api.buyv3(
            amount, ACTIVES, ACTION, expirations, req_id)
        start_t = time.time()
        while global_value.result is None or global_value.order_data is None:
            if time.time() - start_t >= 5:
                logging.error(global_value.order_data["error"])
                return False, None

        return global_value.result, global_value.order_data["id"]

    def check_win(self, id_number):
        """Return amount of deals and win/lose status."""

        while True:
            try:
                order_info = self.get_async_order(id_number)
                if order_info["id"] is not None:
                    break
            except:
                pass

            # Determina el estado de win/lose basado en el profit.
        status = "win" if order_info["profit"] > 0 else "lose"
        return order_info["profit"], status

    @staticmethod
    def last_time(timestamp, period):
        # Divide por 60 para convertir a minutos, usa int() para truncar al entero más cercano (redondear hacia abajo),
        # y luego multiplica por 60 para volver a convertir a segundos.
        timestamp_redondeado = (timestamp // period) * period
        return int(timestamp_redondeado)

    def get_candles(self, ACTIVES, period, end_time, count=9000, count_request=1):
        """
        Realiza múltiples peticiones para obtener datos históricos de velas y los procesa.
        Devuelve un Dataframe ordenado de menor a mayor por la columna 'time'.

        :param ACTIVES: El activo para el cual obtener las velas.
        :param period: El intervalo de tiempo de cada vela en segundos.
        :param count: El número de segundos a obtener en cada petición, max: 9000 = 150 datos.
        :param end_time: El tiempo final para la última vela.
        :param count_request: El número de peticiones para obtener más datos históricos.
        """

        time_sync = self.get_server_timestamp() - period
        time_red = self.last_time(time_sync, period)
        print(time_red)
        data_temp = []
        self.api.candles = data_temp

        if self.api.historyNew is not None:
            data_temp.extend(self.process_data_history(self.api.historyNew, period))

        for i in range(count_request):
            self.api.history_data = None
            while True:
                try:
                    self.api.getcandles(ACTIVES, period, count, time_red)
                    while self.check_connect and self.api.history_data is None:
                        pass
                    if self.api.history_data is not None:
                        data_temp.extend(self.api.history_data)
                        break

                except:
                    logging.error('**error** get_candles need reconnect')
                    # self.connect()

            # Ajusta el tiempo de inicio para la próxima petición
            time_red -= count

        return self.api.candles

    def process_data_history(self, data, period):
        """
        Este método toma datos históricos, los convierte en un DataFrame de pandas, redondea los tiempos al minuto más cercano,
        y calcula los valores OHLC (Open, High, Low, Close) para cada minuto. Luego, convierte el resultado en un diccionario
        y lo devuelve.

        :param dict data: Datos históricos que incluyen marcas de tiempo y precios.
        :param int period: Periodo en minutos
        :return: Un diccionario que contiene los valores OHLC agrupados por minutos redondeados.
        """
        # Crear DataFrame
        df = pd.DataFrame(data['history'], columns=['timestamp', 'price'])
        # Convertir a datetime y redondear al minuto
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='s', utc=True)
        df['datetime'] = df['datetime'].dt.tz_convert(str(local_zone_name))
        df['minute_rounded'] = df['datetime'].dt.floor(f'{period/60}T')

        # Calcular OHLC
        ohlcv = df.groupby('minute_rounded').agg(
            open=('price', 'first'),
            high=('price', 'max'),
            low=('price', 'min'),
            close=('price', 'last')
        ).reset_index()

        ohlcv['time'] = ohlcv['minute_rounded'].apply(lambda x: int(x.timestamp()))
        ohlcv = ohlcv.drop(columns='minute_rounded')

        ohlcv_dict = ohlcv.to_dict(orient='records')

        return ohlcv_dict

    @staticmethod
    def process_candle(candle_data, period):
        """
        Resumen: Este método estático de Python, denominado `process_candle`, toma datos de velas financieras y un período de tiempo específico como entrada.
        Realiza varias operaciones de limpieza y organización de datos utilizando pandas, incluyendo la ordenación por tiempo, eliminación de duplicados,
        y reindexación. Además, verifica si las diferencias de tiempo entre las entradas consecutivas son iguales al período especificado y retorna tanto el DataFrame procesado
        como un booleano indicando si todas las diferencias son iguales al período dado. Este método es útil para preparar y verificar la consistencia de los datos de velas financieras
        para análisis posteriores.

        Procesa los datos de las velas recibidos como entrada.
        Convierte los datos de entrada en un DataFrame de pandas, los ordena por tiempo de forma ascendente,
        elimina duplicados basados en la columna 'time', y reinicia el índice del DataFrame.
        Adicionalmente, verifica si las diferencias de tiempo entre las filas consecutivas son iguales al período especificado,
        asumiendo que el período está dado en segundos, e imprime si todas las diferencias son de 60 segundos.
        :param list candle_data: Datos de las velas a procesar.
        :param int period: El período de tiempo entre las velas, usado para la verificación de diferencias de tiempo.
        :return: DataFrame procesado con los datos de las velas.
        """
        # Convierte los datos en un DataFrame y los añade al DataFrame final
        data_df = pd.DataFrame(candle_data)
        # datos_completos = pd.concat([datos_completos, data_df], ignore_index=True)
        # Procesa los datos obtenidos
        data_df.sort_values(by='time', ascending=True, inplace=True)
        data_df.drop_duplicates(subset='time', keep="first", inplace=True)
        data_df.reset_index(drop=True, inplace=True)
        data_df.fillna(method='ffill', inplace=True)
        data_df.drop(columns='symbol_id', inplace=True)
        # Verificación opcional: Comprueba si las diferencias son todas de 60 segundos (excepto el primer valor NaN)
        diferencias = data_df['time'].diff()
        diff = (diferencias[1:] == period).all()
        return data_df, diff

