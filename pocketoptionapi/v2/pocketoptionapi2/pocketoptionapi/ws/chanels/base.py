"""Module for base IQ Option base websocket chanel."""


class Base(object):
    """Class for base IQ Option websocket chanel."""
    # pylint: disable=too-few-public-methods

    def __init__(self, api):
        """
        :param api: The instance of :class:`pocketoptionapi
            <pocketoptionapi.api.pocketoptionapi>`.
        """
        self.api = api

    def send_websocket_request(self, msg,no_force_send=True):
        """Send request to IQ Option server websocket.
        :returns: The instance of :class:`requests.Response`.
        """
        return self.api.send_websocket_request(msg,no_force_send)
