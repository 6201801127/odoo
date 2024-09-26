#!/usr/bin/python3

import requests
import json

url = "http://localhost:8076/web/login2"
payload = {"params": {
    "login": "admin",
    "password": "admin",
}}
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
# headers = {'Content-type': 'text/html', 'Accept': 'text/plain'}
response = requests.post(url, data=json.dumps(payload), headers=headers)
res = json.loads(response.text)
print('res....', res)

