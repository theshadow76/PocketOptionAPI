from pocketoptionapi.pocket import PocketOptionApi
import time

pocketapi = PocketOptionApi(token="d8fa39dd2f2f58e34e8640fd61f054c2")

data = """42["auth",{"session":"a:4:{s:10:\"session_id\";s:32:\"d8fa39dd2f2f58e34e8640fd61f054c2\";s:10:\"ip_address\";s:10:\"90.36.9.15\";s:10:\"user_agent\";s:120:\"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 OP\";s:13:\"last_activity\";i:1707062743;}6b3f96969615d299c7bbbbb5b2a5ddcd","isDemo":1,"uid":27658142,"platform":1}]"""
pocketapi.connect()
pocketapi.login(init_msg=data)