from pocketoptionapi.ws.chanels.base import Base
import time


class Get_Balances(Base):
    name = "sendMessage"

    def __call__(self):
        """
        :param options_ids: list or int
        """

        data = {"name": "get-balances",
                "version": "1.0"
                }
        print(f"sent balance requests | data: {data}")

        self.send_websocket_request(self.name, data)
