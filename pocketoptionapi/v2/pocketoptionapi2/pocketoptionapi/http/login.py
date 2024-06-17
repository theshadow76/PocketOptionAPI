from pocketoptionapi.http.resource import Resource
import json
class Login(Resource):
 
    def _post(self, data=None, headers=None):
        headers={}
    
        headers = {
        'X-App-Name': 'app_ios',
        'X-Request-Type': 'Api-Request',
        'X-Request-Project': 'bo',
        'Cookie': 'guest_id=1000290216601684147969408361021491595862009238107429568028672977'
        }

        
        return self.api.send_http_request(method="POST", url="https://api.olymptrade.com/v3/user/login-by-password",data=data, headers=headers)
    def __call__(self, username, password,token=None):

      
        data= "{\"data\":{\"email\":\""+username+"\",\"password\":\""+password+"\"}}"
        return self._post(data=str(data))
 