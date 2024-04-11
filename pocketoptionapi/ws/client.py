import asyncio
from datetime import datetime, timedelta, timezone

import websocket
import websockets
import json
import logging
import ssl

# Suponiendo la existencia de estos módulos basados en tu código original
import pocketoptionapi.constants as OP_code
import pocketoptionapi.global_value as global_value
from pocketoptionapi.constants import REGION
from pocketoptionapi.ws.objects.timesync import TimeSync

logger = logging.getLogger(__name__)

timesync = TimeSync()


async def on_open():  # pylint: disable=unused-argument
    """Method to process websocket open."""
    print("CONECTADO CON EXITO")
    logger = logging.getLogger(__name__)
    logger.debug("Websocket client connected.")
    global_value.websocket_is_connected = True


async def send_pin(ws):
    while global_value.websocket_is_connected is False:
        await asyncio.sleep(0.1)
    pass
    while True:
        await asyncio.sleep(20)
        await ws.send('42["ps"]')


class WebsocketClient(object):
    def __init__(self, api) -> None:
        """
        Inicializa el cliente WebSocket.


        :param ssid: El ID de sesión para la autenticación.
        :param url: La URL del WebSocket a la que conectarse.
        """

        self.updateHistoryNew = None
        self.updateStream = None
        self.history_data_ready = None
        self.successcloseOrder = False
        self.api = api
        self.message = None
        self.url = None
        self.ssid = global_value.SSID
        self.websocket = None
        self.region = REGION()
        self.loop = asyncio.get_event_loop()
        self.esperar_segundo_mensaje = False
        self.recibido_updateClosedDeals = False

    async def reconnect(self):
        regs = self.region.get_regions()
        for i in regs:
            print(f"Reconnecting to {i}...")
            async with websockets.connect(i, extra_headers={"Origin": "https://m.pocketoption.com"}) as ws:

                print("Conectado a: ", i)
                self.websocket = ws
                self.url = i
                on_message_task = asyncio.create_task(self.websocket_listener(ws))
                sender_task = asyncio.create_task(send_pin(ws))
                message_task = asyncio.create_task(self.send_message(self.message))
                await asyncio.gather(on_message_task, sender_task, message_task)


    async def websocket_listener(self, ws):
        async for message in ws:
            await self.on_message(message)

    async def connect(self):
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        while global_value.websocket_is_connected is False:
            for url in self.region.get_regions(True):
                print(url)
                try:
                    async with websockets.connect(url, extra_headers={"Origin": "https://m.pocketoption.com"}) as ws:

                        print("Conectado a: ", url)
                        self.websocket = ws
                        self.url = url
                        on_message_task = asyncio.create_task(self.websocket_listener(ws))
                        sender_task = asyncio.create_task(send_pin(ws))
                        message_task = asyncio.create_task(self.send_message(self.message))
                        await asyncio.gather(on_message_task, sender_task, message_task)
                except websockets.ConnectionClosed as e:
                    await self.on_close(e)
                except Exception as e:
                    await self.on_error(e)

            return True

    async def send_message(self, message):
        while global_value.websocket_is_connected is False:
            await asyncio.sleep(0.1)
        pass

        self.message = message

        if global_value.websocket_is_connected:

            if message is not None:
                await self.websocket.send(message)

        else:
            logging.warning("WebSocked not connected")

    @staticmethod
    def dict_queue_add(self, dict, maxdict, key1, key2, key3, value):
        if key3 in dict[key1][key2]:
            dict[key1][key2][key3] = value
        else:
            while True:
                try:
                    dic_size = len(dict[key1][key2])
                except:
                    dic_size = 0
                if dic_size < maxdict:
                    dict[key1][key2][key3] = value
                    break
                else:
                    # del mini key
                    del dict[key1][key2][sorted(dict[key1][key2].keys(), reverse=False)[0]]

    async def on_message(self, message):  # pylint: disable=unused-argument
        """Method to process websocket messages."""
        # global_value.ssl_Mutual_exclusion = True
        logger = logging.getLogger(__name__)
        logger.debug(message)

        # message = json.loads(str(message))

        if type(message) is bytes:
            # Paso 1: Decodificar los bytes a una cadena de texto (string)
            message = message.decode('utf-8')
            message = json.loads(message)

            # print(message, type(message))  # [:1000000])
            if "balance" in message:
                global_value.balance_id = message["uid"]
                global_value.balance = message["balance"]
                global_value.balance_type = message["isDemo"]

                data = {
                    "balance_id" :  message["uid"],
                    "balance" : message["balance"],
                    "balance_type" : message["isDemo"]
                }

                with open("balance.json", "w") as f:
                    json.dump(data, f)

            elif "requestId" in message and message["requestId"] == 'buy':
                global_value.order_data = message

                # Supongamos que este es el segundo mensaje de interés basado en tu lógica
            elif self.esperar_segundo_mensaje and isinstance(message, list):
                self.esperar_segundo_mensaje = False  # Restablecer para futuros mensajes
                self.recibido_updateClosedDeals = False  # Restablecer el estado

            elif self.esperar_segundo_mensaje and isinstance(message, dict) and self.successcloseOrder:
                self.api.order_async = message
                self.successcloseOrder = False  # Restablecer para futuros mensajes
                self.esperar_segundo_mensaje = False  # Restablecer el estado

            elif self.history_data_ready and isinstance(message, dict):
                self.history_data_ready = False
                self.api.history_data = message["data"]

            elif self.updateStream and isinstance(message, list):
                self.updateStream = False
                self.api.timesync.server_timestamp = message[0][1]
                # print("server_timestamp asignado:", timesync.server_timestamp)

            elif self.updateHistoryNew and isinstance(message, dict):
                self.updateHistoryNew = False
                self.api.historyNew = message

            return

        else:
            pass
            # print(message)

        if message.startswith('0{"sid":"'):
            # print(f"{self.url.split('/')[2]} got 0 sid send 40")
            await self.websocket.send("40")
        elif message == "2":
            # print(f"{self.url.split('/')[2]} got 2 send 3")
            await self.websocket.send("3")

        elif message.startswith('40{"sid":"'):
            # print(f"{self.url.split('/')[2]} got 40 sid send session")
            await self.websocket.send(self.ssid)

        elif message.startswith('451-['):
            # Eliminar el prefijo numérico y el guion para obtener el JSON válido
            json_part = message.split("-", 1)[1]

            # Convertir la parte JSON a un objeto Python
            message = json.loads(json_part)

            if message[0] == "successauth":
                await on_open()
            elif message[0] == "successupdateBalance":
                global_value.balance_updated = True
            elif message[0] == "successopenOrder":
                global_value.result = True

                # Si es el primer mensaje de interés
            elif message[0] == "updateClosedDeals":
                # Establecemos que hemos recibido el primer mensaje de interés
                self.recibido_updateClosedDeals = True
                self.esperar_segundo_mensaje = True  # Establecemos que esperamos el segundo mensaje de interés
                await self.websocket.send('42["changeSymbol",{"asset":"AUDNZD_otc","period":60}]')

            elif message[0] == "successcloseOrder":
                self.successcloseOrder = True
                self.esperar_segundo_mensaje = True  # Establecemos que esperamos el segundo mensaje de interés

            elif message[0] == "loadHistoryPeriod":
                self.history_data_ready = True

            elif message[0] == "updateStream":
                self.updateStream = True

            elif message[0] == "updateHistoryNew":
                self.updateHistoryNew = True

    async def on_error(self, error):  # pylint: disable=unused-argument
        """Method to process websocket errors."""
        logger = logging.getLogger(__name__)
        logger.error(error)
        try:
            self.reconnect()
        except:
            global_value.websocket_error_reason = str(error)
            global_value.check_websocket_if_error = True

    async def on_close(self, error):  # pylint: disable=unused-argument
        """Method to process websocket close."""
        logger = logging.getLogger(__name__)
        logger.debug("Websocket connection closed.")
        try:
            self.reconnect()
        except:
            global_value.websocket_is_connected = False
