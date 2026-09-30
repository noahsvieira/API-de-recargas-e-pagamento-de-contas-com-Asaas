import httpx
from app.config import ASAAS_API_KEY, ASAAS_BASE_URL


class AsaasError(Exception):
    def __init__(self, status_code: int, detalhe):
        self.status_code = status_code
        self.detalhe = detalhe


async def _chamar(metodo: str, caminho: str, corpo: dict | None = None):
    headers = {
        "access_token": ASAAS_API_KEY,
        "Content-Type": "application/json",
        "User-Agent": "portfolio-api-recargas",
    }
    try:
        async with httpx.AsyncClient(base_url=ASAAS_BASE_URL, timeout=60) as client:
            resp = await client.request(metodo, caminho, json=corpo, headers=headers)
    except httpx.RequestError as e:
        print("ERRO DE CONEXÃO DETALHADO:", repr(e))
        raise AsaasError(502, f"Não foi possível falar com o Asaas: {e}")

    if resp.status_code >= 400:
        try:
            detalhe = resp.json()
        except ValueError:
            detalhe = resp.text
        raise AsaasError(resp.status_code, detalhe)
    return resp.json()


async def criar_recarga(telefone: str, valor: float):
    return await _chamar("POST", "/mobilePhoneRecharges",
                         {"phoneNumber": telefone, "value": valor})


async def consultar_recarga(recarga_id: str):
    return await _chamar("GET", f"/mobilePhoneRecharges/{recarga_id}")


async def pagar_conta(linha_digitavel: str, descricao=None, data_agendamento=None):
    corpo = {"identificationField": linha_digitavel}
    if descricao:
        corpo["description"] = descricao
    if data_agendamento:
        corpo["scheduleDate"] = data_agendamento
    return await _chamar("POST", "/bill", corpo)


async def consultar_conta(conta_id: str):
    return await _chamar("GET", f"/bill/{conta_id}")