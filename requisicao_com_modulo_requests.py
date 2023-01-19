#Como realizar requisições via modulo requests.
from requests.auth import HTTPBasicAuth
import requests

resultado = requests.get('http://localhost:7777/login', auth=('Anderson', '123456'))

print(resultado.json())

resultado_autores = requests.get('http://localhost:7777/autores', headers={'x-access-token': resultado.json()['token']})

print(resultado_autores.json())