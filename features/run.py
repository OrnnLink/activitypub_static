import requests

url = 'https://sdlay.netlify.app/user-info/ylay/outbox.json'
response = requests.get(url, headers={"accept": "application/activity+json" }) 
if response.ok:
   print(response.text)
else:
   print(response.reason)
