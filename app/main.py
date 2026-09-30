from fastapi import FastAPI, Depends, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from app import asaas_client as asaas
from app.asaas_client import AsaasError
from app.config import MINHA_API_KEY, ASAAS_WEBHOOK_TOKEN
from app.schemas import RecargaIn, ContaIn

app = FastAPI(title="API de Recargas e Pagamento de Contas")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

eventos_processados: set[str] = set()  # em produção, use banco de dados


def exigir_chave(x_api_key: str = Header(default="")):
    if not MINHA_API_KEY or x_api_key != MINHA_API_KEY:
        raise HTTPException(status_code=401, detail="Chave de API inválida")


@app.exception_handler(AsaasError)
async def tratar_erro_asaas(request: Request, exc: AsaasError):
    return JSONResponse(status_code=exc.status_code,
                        content={"erro": "Falha no Asaas", "detalhe": exc.detalhe})


@app.get("/saude")
async def saude():
    return {"status": "ok"}


@app.post("/recargas", dependencies=[Depends(exigir_chave)])
async def solicitar_recarga(dados: RecargaIn):
    return await asaas.criar_recarga(dados.telefone, dados.valor)


@app.get("/recargas/{recarga_id}", dependencies=[Depends(exigir_chave)])
async def ver_recarga(recarga_id: str):
    return await asaas.consultar_recarga(recarga_id)


@app.post("/contas", dependencies=[Depends(exigir_chave)])
async def pagar(dados: ContaIn):
    return await asaas.pagar_conta(dados.linha_digitavel, dados.descricao,
                                   dados.data_agendamento)


@app.get("/contas/{conta_id}", dependencies=[Depends(exigir_chave)])
async def ver_conta(conta_id: str):
    return await asaas.consultar_conta(conta_id)


@app.post("/webhooks/asaas")
async def webhook(request: Request, asaas_access_token: str = Header(default="")):
    if asaas_access_token != ASAAS_WEBHOOK_TOKEN:
        raise HTTPException(status_code=401, detail="Token inválido")

    evento = await request.json()
    evento_id = evento.get("id")

    if evento_id in eventos_processados:      # idempotência
        return {"recebido": True, "duplicado": True}
    eventos_processados.add(evento_id)

    print("Evento recebido:", evento.get("event"))
    return {"recebido": True}