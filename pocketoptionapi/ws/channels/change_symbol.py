"""Module for PocketOption change symbol websocket chanel."""

from pocketoptionapi.ws.channels.base import Base
import time
import random


class ChangeSymbol(Base):
    """Class for Pocket option change symbol websocket chanel."""
    # pylint: disable=too-few-public-methods

    name = "sendMessage"

    def __call__(self, active_id, interval):
        """Method to send message to candles websocket chanel.

        :param active_id: The active/asset identifier.
        :param interval: The candle duration (timeframe for the candles).
        """

        data_stream = ["changeSymbol", {
            "asset": active_id,
            "period": interval}]

        self.send_websocket_request(self.name, data_stream)
