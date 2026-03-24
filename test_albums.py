import requests

url = "https://jsonplaceholder.typicode.com/albums"

payload = ""
headers = {}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
