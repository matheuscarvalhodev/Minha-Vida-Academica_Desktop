import requests
import json
from requests.auth import HTTPBasicAuth

url = "http://localhost:5000/api.paem"

from src.infra.conexao import login

token, res = login("admin", "admin")

headers = {"Authorization": f"Bearer {token}"}
r = requests.get(url + f"/discente_vacinacao?matricula={'201800032'}", headers=headers)
lista = r.json()
quantidade = lista["quantidade_vacinas"]
fabricante = lista["fabricante"].lower()

print(fabricante)
