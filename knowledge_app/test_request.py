import requests

resp = requests.post('http://127.0.0.1:5000/generate', data={'query':'productivity','platform':'Facebook'})
print('status', resp.status_code)
print(resp.text)
