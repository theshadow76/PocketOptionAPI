"""Module for Pocket Option API."""
import asyncio
import datetime
import time
import json
import logging
import threading
import requests
import ssl
import atexit
from collections import deque
from pocketoptionapi.ws.client import WebsocketClient
from pocketoptionapi.ws.channels.get_balances import *

from pocketoptionapi.ws.channels.ssid import Ssid
# from pocketoptionapi.ws.channels.subscribe import *
# from pocketoptionapi.ws.channels.unsubscribe import *
# from pocketoptionapi.ws.channels.setactives import SetActives
from pocketoptionapi.ws.channels.candles import GetCandles
# from pocketoptionapi.ws.channels.buyv2 import Buyv2
from pocketoptionapi.ws.channels.buyv3 import *
# from pocketoptionapi.ws.channels.user import *
# from pocketoptionapi.ws.channels.api_game_betinfo import Game_betinfo
# from pocketoptionapi.ws.channels.instruments import Get_instruments
# from pocketoptionapi.ws.channels.get_financial_information import GetFinancialInformation
# from pocketoptionapi.ws.channels.strike_list import Strike_list
# from pocketoptionapi.ws.channels.leaderboard import Leader_Board

# from pocketoptionapi.ws.channels.traders_mood import Traders_mood_subscribe
# from pocketoptionapi.ws.channels.traders_mood import Traders_mood_unsubscribe
# from pocketoptionapi.ws.channels.buy_place_order_temp import Buy_place_order_temp
# from pocketoptionapi.ws.channels.get_order import Get_order
# from pocketoptionapi.ws.channels.get_deferred_orders import GetDeferredOrders
# from pocketoptionapi.ws.channels.get_positions import *

# from pocketoptionapi.ws.channels.get_available_leverages import Get_available_leverages
# from pocketoptionapi.ws.channels.cancel_order import Cancel_order
# from pocketoptionapi.ws.channels.close_position import Close_position
# from pocketoptionapi.ws.channels.get_overnight_fee import Get_overnight_fee
# from pocketoptionapi.ws.channels.heartbeat import Heartbeat

# from pocketoptionapi.ws.channels.digital_option import *
# from pocketoptionapi.ws.channels.api_game_getoptions import *
# from pocketoptionapi.ws.channels.sell_option import Sell_Option
# from pocketoptionapi.ws.channels.change_tpsl import Change_Tpsl
# from pocketoptionapi.ws.channels.change_auto_margin_call import ChangeAutoMarginCall

from pocketoptionapi.ws.objects.timesync import TimeSync
# from pocketoptionapi.ws.objects.profile import Profile
from pocketoptionapi.ws.objects.candles import Candles
# from pocketoptionapi.ws.objects.listinfodata import ListInfoData
# from pocketoptionapi.ws.objects.betinfo import Game_betinfo_data
import pocketoptionapi.global_value as global_value
from pocketoptionapi.ws.channels.change_symbol import ChangeSymbol
from collections import defaultdict
from pocketoptionapi.ws.objects.time_sync import TimeSynchronizer


def nested_dict(n, type):
    if n == 1:
        return defaultdict(type)
    else:
        return defaultdict(lambda: nested_dict(n - 1, type))


# InsecureRequestWarning: Unverified HTTPS request is being made.
# Adding certificate verification is strongly advised.
# See: https://urllib3.readthedocs.org/en/latest/security.html


class PocketOptionAPI(object):  # pylint: disable=too-many-instance-attributes
    """Class for communication with Pocket Option API."""

    # pylint: disable=too-many-public-methods
    socket_option_opened = {}
    time_sync = TimeSync()
    sync = TimeSynchronizer()
    timesync = None
    # pylint: disable=too-many-arguments
    # profile = Profile()
    candles = Candles()
    # listinfodata = ListInfoData()
    api_option_init_all_result = []
    api_option_init_all_result_v2 = []
    # for digital
    underlying_list_data = None
    position_changed = None
    instrument_quites_generated_data = nested_dict(2, dict)
    instrument_quotes_generated_raw_data = nested_dict(2, dict)
    instrument_quites_generated_timestamp = nested_dict(2, dict)
    strike_list = None
    leaderboard_deals_client = None
    # position_changed_data = nested_dict(2, dict)
    # microserviceName_binary_options_name_option=nested_dict(2,dict)
    order_async = None
    # game_betinfo = Game_betinfo_data()
    instruments = None
    financial_information = None
    buy_id = None
    buy_order_id = None
    traders_mood = {}  # get hight(put) %
    order_data = None
    positions = None
    position = None
    deferred_orders = None
    position_history = None
    position_history_v2 = None
    available_leverages = None
    order_canceled = None
    close_position_data = None
    overnight_fee = None
    # ---for real time
    digital_option_placed_id = None
    live_deal_data = nested_dict(3, deque)

    subscribe_commission_changed_data = nested_dict(2, dict)
    real_time_candles = nested_dict(3, dict)
    real_time_candles_maxdict_table = nested_dict(2, dict)
    candle_generated_check = nested_dict(2, dict)
    candle_generated_all_size_check = nested_dict(1, dict)
    # ---for api_game_getoptions_result
    api_game_getoptions_result = None
    sold_options_respond = None
    tpsl_changed_respond = None
    auto_margin_call_changed_respond = None
    top_assets_updated_data = {}
    get_options_v2_data = None
    # --for binary option multi buy
    buy_multi_result = None
    buy_multi_option = {}
    #
    result = None
    training_balance_reset_request = None
    balances_raw = None
    user_profile_client = None
    leaderboard_userinfo_deals_client = None
    users_availability = None
    history_data = None
    historyNew = None
    server_timestamp = None
    sync_datetime = None

    # ------------------

    def __init__(self, proxies=None):
        """
        :param dict proxies: (optional) The http request proxies.
        """
        self.websocket_client = None
        self.websocket_thread = None
        # self.wss_url = "wss://api-us-north.po.market/socket.io/?EIO=4&transport=websocket"
        self.session = requests.Session()
        self.session.verify = False
        self.session.trust_env = False
        self.proxies = proxies
        # is used to determine if a buyOrder was set  or failed. If
        # it is None, there had been no buy order yet or just send.
        # If it is false, the last failed
        # If it is true, the last buy order was successful
        self.buy_successful = None
        self.loop = asyncio.get_event_loop()
        self.websocket_client = WebsocketClient(self)

    @property
    def websocket(self):
        """Property to get websocket.

        :returns: The instance of :class:`WebSocket <websocket.WebSocket>`.
        """
        return self.websocket_client

    def send_websocket_request(self, name, msg, request_id="", no_force_send=True):
        """Send websocket request to IQ Option server.

        :param no_force_send:
        :param request_id:
        :param str name: The websocket request name.
        :param dict msg: The websocket request msg.
        """

        logger = logging.getLogger(__name__)

        # data = json.dumps(dict(name=name, msg=msg, request_id=request_id))
        data = f'42{json.dumps(msg)}'

        while (global_value.ssl_Mutual_exclusion or global_value.ssl_Mutual_exclusion_write) and no_force_send:
            pass
        global_value.ssl_Mutual_exclusion_write = True

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Ejecutar la corutina connect dentro del bucle de eventos del nuevo hilo
        loop.run_until_complete(self.websocket.send_message(data))

        logger.debug(data)
        global_value.ssl_Mutual_exclusion_write = False

    def start_websocket(self):
        global_value.websocket_is_connected = False
        global_value.check_websocket_if_error = False
        global_value.websocket_error_reason = None

        # Obtener o crear un nuevo bucle de eventos para este hilo
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Ejecutar la corutina connect dentro del bucle de eventos del nuevo hilo
        loop.run_until_complete(self.websocket.connect())
        loop.run_forever()

        while True:
            try:
                if global_value.check_websocket_if_error:
                    return False, global_value.websocket_error_reason
                if global_value.websocket_is_connected is False:
                    return False, "Websocket connection closed."
                elif global_value.websocket_is_connected is True:
                    return True, None

            except:
                pass
            pass

    def connect(self):
        """Method for connection to Pocket Option API."""

        global_value.ssl_Mutual_exclusion = False
        global_value.ssl_Mutual_exclusion_write = False

        check_websocket, websocket_reason = self.start_websocket()

        if not check_websocket:
            return check_websocket, websocket_reason

        self.time_sync.server_timestamps = None
        while True:
            try:
                if self.time_sync.server_timestamps is not None:
                    break
            except:
                pass
        return True, None

    async def close(self, error=None):
        await self.websocket.on_close(error)
        self.websocket_thread.join()

    def websocket_alive(self):
        return self.websocket_thread.is_alive()

    @property
    def get_balances(self):
        """Property for get IQ Option http getprofile resource.

        :returns: The instance of :class:`Login
            <iqoptionapi.http.getprofile.Getprofile>`.
        """
        return Get_Balances(self)

        # ____________for_______binary_______option_____________

    @property
    def buyv3(self):
        return Buyv3(self)

    @property
    def getcandles(self):
        """Property for get IQ Option websocket candles chanel.

        :returns: The instance of :class:`GetCandles
            <pocketoptionapi.ws.channels.candles.GetCandles>`.
        """
        return GetCandles(self)

    @property
    def change_symbol(self):
        """Property for get Pocket Option websocket change_symbol chanel.

        :returns: The instance of :class:`ChangeSymbol
            <iqoptionapi.ws.channels.change_symbol.ChangeSymbol>`.
        """
        return ChangeSymbol(self)

    @property
    def synced_datetime(self):
        try:
            if self.time_sync is not None:
                self.sync.synchronize(self.time_sync.server_timestamp)
                self.sync_datetime = self.sync.get_synced_datetime()
            else:
                logging.error("timesync no está establecido")
                self.sync_datetime = None
        except Exception as e:
            logging.error(e)
            self.sync_datetime = None

        return self.sync_datetime
