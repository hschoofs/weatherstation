import requests
import time


url = 'https://weather.eolab.de/node-red/input/weather-data'
myobj = {'somekey': 'somevalue'}

x = requests.post(url, data = myobj, headers = {"Authorization": "Basic d2VhdGhlcjpXZW9sYWJTMjA="})
print("sent")
print(x)
time.sleep(5)
