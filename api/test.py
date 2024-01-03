import requests

response = requests.get("http://127.0.0.1:5000/api/get_username/nam12")
data = response.json()
print(data)
