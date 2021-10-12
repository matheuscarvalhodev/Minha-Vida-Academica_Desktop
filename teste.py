import requests
import json
from requests.auth import HTTPBasicAuth

url = "http://localhost:5000/api.paem"

from src.infra.conexao import login

token, res = login("admin", "admin")

headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
res = requests.get(url + "/solicitacoes_acessos", headers=headers)
lista = res.json()
n_matricula = str(201800032)
data = ""
verificacao = ""
for i in lista:
    if n_matricula in i.values():
        verificacao = True
        data = i
    else:
        verificacao = False

if verificacao is True:
    id_solicitacao = data["id"]
    area_solicitada = data["recurso_campus"]
    dados = dict()
    dados["nome_aluno"] = data["discente"]
    dados["matricula"] = data["matricula"]
    dados["para_si"] = data["para_si"]
    dados["data_solicitacao"] = data["data"]
    dados["hora_ini"] = data["hora_inicio"]
    dados["hora_fim"] = data["hora_fim"]
    dados["status_acesso"] = data["status_acesso"]
    print(dados)
