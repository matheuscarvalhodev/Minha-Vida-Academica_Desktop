import requests
import json
from requests.auth import HTTPBasicAuth

url = "http://webservicepaem-env.eba-mkyswznu.sa-east-1.elasticbeanstalk.com/api.paem"

from src.infra.conexao import login

token, res = login("admin", "admin")

headers = {"Authorization": f"Bearer {token}"}
r = requests.get(url + f"/usuarios/usuario", headers=headers)
lista = r.json()
tipo = lista["tipo"]

print(tipo)
