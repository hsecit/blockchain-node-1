import requests
import json
DATA_SERVER = "http://192.168.1.5"
def send_it_now(data):
    print(data)
    url = "{}/api/bank/check_card".format(DATA_SERVER)
    headers = {'Content-Type': "application/json"}
    response = requests.post(url,data=json.dumps(data))
    return response.json()
    