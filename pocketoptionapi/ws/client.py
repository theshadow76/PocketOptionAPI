import asyncio
from datetime import datetime, timedelta, timezone

import websockets
import json
import logging
import ssl

# Suponiendo la existencia de estos módulos basados en tu código original
import pocketoptionapi.constants as OP_code
import pocketoptionapi.global_value as global_value
from pocketoptionapi.constants import REGION
from pocketoptionapi.ws.objects.timesync import TimeSync
from pocketoptionapi.ws.objects.time_sync import TimeSynchronizer

logger = logging.getLogger(__name__)

timesync = TimeSync()
sync = TimeSynchronizer()


async def on_open():  # pylint: disable=unused-argument
    """Method to process websocket open."""
    print("CONNECTED SUCCESSFUL")
    logger.debug("Websocket client connected.")
    global_value.websocket_is_connected = True


async def send_ping(ws):
    while global_value.websocket_is_connected is False:
        await asyncio.sleep(0.1)
    pass
    while True:
        await asyncio.sleep(20)
        await ws.send('42["ps"]')


async def process_message(message):
    try:
        data = json.loads(message)
        print(f"Received message: {data}")

        # Procesa el mensaje dependiendo del tipo
        if isinstance(data, dict) and 'uid' in data:
            uid = data['uid']
            print(f"UID: {uid}")
        elif isinstance(data, list) and len(data) > 0:
            event_type = data[0]
            event_data = data[1]
            print(f"Event type: {event_type}, Event data: {event_data}")
            # Aquí puedes añadir más lógica para manejar diferentes tipos de eventos

    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
    except KeyError as e:
        print(f"Key error: {e}")
    except Exception as e:
        print(f"Error processing message: {e}")


class WebsocketClient(object):
    def __init__(self, api) -> None:
        """
        Inicializa el cliente WebSocket.

        :param api: Instancia de la clase PocketOptionApi
        """

        self.updateHistoryNew = None
        self.updateStream = None
        self.history_data_ready = None
        self.successCloseOrder = False
        self.api = api
        self.message = None
        self.url = None
        self.ssid = global_value.SSID
        self.websocket = None
        self.region = REGION()
        self.loop = asyncio.get_event_loop()
        self.wait_second_message = False
        self._updateClosedDeals = False

    async def websocket_listener(self, ws):
        try:
            async for message in ws:
                await self.on_message(message)
        except Exception as e:
            logging.warning(f"Error occurred: {e}")

    async def connect(self):
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        try:
            await self.api.close()
        except:
            pass

        while not global_value.websocket_is_connected:
            for url in self.region.get_regions(True):
                print(url)
                try:
                    async with websockets.connect(
                            url,
                            ssl=ssl_context,
                            extra_headers={"Origin": "https://pocketoption.com", "Cache-Control": "no-cache"},
                            user_agent_header="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                                              "like Gecko) Chrome/124.0.0.0 Safari/537.36"
                    ) as ws:

                        # print("Connected a: ", url)
                        self.websocket = ws
                        self.url = url
                        global_value.websocket_is_connected = True

                        # Crear y ejecutar tareas
                        # process_message_task = asyncio.create_task(process_message(self.message))
                        on_message_task = asyncio.create_task(self.websocket_listener(ws))
                        sender_task = asyncio.create_task(self.send_message(self.message))
                        ping_task = asyncio.create_task(send_ping(ws))

                        await asyncio.gather(on_message_task, sender_task, ping_task)

                except websockets.ConnectionClosed as e:
                    global_value.websocket_is_connected = False
                    await self.on_close(e)
                    logger.warning("Trying another server")

                except Exception as e:
                    global_value.websocket_is_connected = False
                    await self.on_error(e)

            await asyncio.sleep(1)  # Esperar antes de intentar reconectar

        return True

    async def send_message(self, message):
        while global_value.websocket_is_connected is False:
            await asyncio.sleep(0.1)

        self.message = message

        if global_value.websocket_is_connected and message is not None:
            try:
                await self.websocket.send(message)
            except Exception as e:
                logger.warning(f"Error sending message: {e}")
        elif message is not None:
            logger.warning("WebSocket not connected")

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
        logger.debug(message)

        if type(message) is bytes:
            message = message.decode('utf-8')
            message = json.loads(message)

            # print(message, type(message))
            if "balance" in message:
                if "uid" in message:
                    global_value.balance_id = message["uid"]
                global_value.balance = message["balance"]
                global_value.balance_type = message["isDemo"]

            elif "requestId" in message and message["requestId"] == 'buy':
                global_value.order_data = message

            elif self.wait_second_message and isinstance(message, list):
                self.wait_second_message = False  # Restablecer para futuros mensajes
                self._updateClosedDeals = False  # Restablecer el estado

            elif isinstance(message, dict) and self.successCloseOrder:
                self.api.order_async = message
                self.successCloseOrder = False  # Restablecer para futuros mensajes

            elif self.history_data_ready and isinstance(message, dict):
                self.history_data_ready = False
                self.api.history_data = message["data"]

            elif self.updateStream and isinstance(message, list):
                self.updateStream = False
                self.api.time_sync.server_timestamp = message[0][1]

            elif self.updateHistoryNew and isinstance(message, dict):
                self.updateHistoryNew = False
                self.api.historyNew = message

            return

        else:
            pass
            # print(message)

        if message.startswith('0') and "sid" in message:
            await self.websocket.send("40")

        elif message == "2":
            await self.websocket.send("3")

        elif "40" and "sid" in message:
            await self.websocket.send(self.ssid)

        elif message.startswith('451-['):
            json_part = message.split("-", 1)[1]  # Eliminar el prefijo numérico y el guion para obtener el JSON válido

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
                self._updateClosedDeals = True
                self.wait_second_message = True  # Establecemos que esperamos el segundo mensaje de interés
                await self.websocket.send('42["changeSymbol",{"asset":"AUDNZD_otc","period":60}]')

            elif message[0] == "successcloseOrder":
                self.successCloseOrder = True
                self.wait_second_message = True  # Establecemos que esperamos el segundo mensaje de interés

            elif message[0] == "loadHistoryPeriod":
                self.history_data_ready = True

            elif message[0] == "updateStream":
                self.updateStream = True

            elif message[0] == "updateHistoryNew":
                self.updateHistoryNew = True
                # self.api.historyNew = None

        elif message.startswith("42") and "NotAuthorized" in message:
            logging.error("User not Authorized: Please Change SSID for one valid")
            global_value.ssl_Mutual_exclusion = False
            await self.websocket.close()

    async def on_error(self, error):  # pylint: disable=unused-argument
        logger.error(error)
        global_value.websocket_error_reason = str(error)
        global_value.check_websocket_if_error = True

    async def on_close(self, error):  # pylint: disable=unused-argument
        # logger.debug("Websocket connection closed.")
        # logger.warning(f"Websocket connection closed. Reason: {error}")
        global_value.websocket_is_connected = False
