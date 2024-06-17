 
class Resource(object):
 
    def __init__(self, api):
 
        self.api = api

    def send_http_request(self, method, data=None, params=None, headers=None):
 
        return self.api.send_http_request(self, method, data=data, params=params, headers=headers)
