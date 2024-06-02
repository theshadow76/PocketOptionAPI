import datetime
import json
import time
from pocketoptionapi.ws.channels.base import Base
import logging
import pocketoptionapi.global_value as global_value
from pocketoptionapi.expiration import get_expiration_time


class Buyv3(Base):
    name = "sendMessage"

    def __call__(self, amount, active, direction, duration, request_id):

        # thank Darth-Carrotpie's code
        # https://github.com/Lu-Yi-Hsun/iqoptionapi/issues/6
        # exp = get_expiration_time(int(self.api.timesync.server_timestamps), duration)
        """if idx < 5:
            option = 3  # "turbo"
        else:
            option = 1  # "binary"""
        # Construir el diccionario
        data_dict = {
            "asset": active,
            "amount": amount,
            "action": direction,
            "isDemo": 1,
            "requestId": request_id,
            "optionType": 100,
            "time": duration
        }

        message = ["openOrder", data_dict]

        self.send_websocket_request(self.name, message, str(request_id))


class Buyv3_by_raw_expired(Base):
    name = "sendMessage"

    def __call__(self, price, active, direction, option, expired, request_id):

        # thank Darth-Carrotpie's code
        # https://github.com/Lu-Yi-Hsun/iqoptionapi/issues/6

        if option == "turbo":
            option_id = 3  # "turbo"
        elif option == "binary":
            option_id = 1  # "binary"
        data = {
            "body": {"price": price,
                     "active_id": active,
                     "expired": int(expired),
                     "direction": direction.lower(),
                     "option_type_id": option_id,
                     "user_balance_id": int(global_value.balance_id)
                     },
            "name": "binary-options.open-option",
            "version": "1.0"
        }
        self.send_websocket_request(self.name, data, str(request_id))
