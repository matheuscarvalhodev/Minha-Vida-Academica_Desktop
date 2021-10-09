import requests
import json
from requests.auth import HTTPBasicAuth
from datetime import datetime

url = "http://localhost:5000/api.paem"
# url = "http://webservicepaem-env.eba-mkyswznu.sa-east-1.elasticbeanstalk.com/api.paem/"


def login(usuario: str = None, senha: str = None):
    resposta = ""
    try:
        autenticacao = HTTPBasicAuth(usuario, senha)
        response = requests.post(url + "/auth", auth=autenticacao)
        res = str(response)[10:15]
        token = ""
        if res == "[200]":
            token = json.loads(response.content).get("token")
            resposta = "valido"
            return token, resposta
        elif res == "[401]":
            resposta = "invalido"
            return "", resposta

    except:
        resposta = "nao conectou"
        return "", resposta


def solicita_dados(token: str = None, n_matricula: str = None):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    res = requests.get(url + "/solicitacoes_acessos", headers=headers)
    lista = res.json()
    n_matricula = str(n_matricula)
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
        return dados, id_solicitacao, area_solicitada, verificacao
    else:
        return "", "", "", verificacao


def enviar_dados(token: str = None, n_matricula: str = None, dicio: object = None):
    entrada = dicio["entrada"]
    saida = dicio["saida"]
    temperatura = dicio["temperatura"]
    _, id_solicitacao, _, _ = solicita_dados(token, n_matricula)
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    r = requests.get(url + "/acessos_permitidos", headers=headers)
    lista = r.json()
    id_acesso = lista[len(lista) - 1]["id_acesso_permitido"]
    id_acesso += 1
    dict_dados = {
        "id_acesso_permitido": id_acesso,
        "hora_entrada": entrada,
        "hora_saida": saida,
        "temperatura": temperatura,
        "solicitacao_acesso_id_solicitacao_acesso": id_solicitacao,
    }
    r = requests.post(
        url + "/acessos_permitidos/acesso_permitido",
        data=json.dumps(dict_dados),
        headers=headers,
    )
    return


def ponto(matricula: str = None, token: str = None):

    dados, id_solicitacao, _, _ = solicita_dados(token, matricula)
    nome_usuario = dados["nome_aluno"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    r = requests.get(url + "/acessos_permitidos", headers=headers)
    lista = r.json()

    id_acesso_permitido = ""
    hora_saida = ""

    for solicitacao in lista:
        if id_solicitacao in solicitacao.values():
            id_acesso_permitido = solicitacao["id_acesso_permitido"]
            hora_saida = solicitacao["hora_saida"]

    if hora_saida == "00:00:00":
        hd = datetime.now()
        horario_atual = hd.strftime("%H:%M:%S")
        dict_dados = {
            "id_acesso_permitido": id_acesso_permitido,
            "hora_saida": horario_atual,
        }
        r = requests.put(
            url + "/acessos_permitidos/acesso_permitido",
            data=json.dumps(dict_dados),
            headers=headers,
        )
        return "Positivo", nome_usuario, horario_atual

    else:
        return "Negativo", " ", " "


def verifica_vacinacao(token: str = None, matricula: str = None):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(
        url + f"/discente_vacinacao?matricula={matricula}", headers=headers
    )
    lista = r.json()
    quantidade = lista["quantidade_vacinas"]

    return quantidade


def verifica_tipo(token: str = None):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url + f"/usuarios/usuario", headers=headers)
    lista = r.json()
    tipo = lista["tipo"]
    return tipo
