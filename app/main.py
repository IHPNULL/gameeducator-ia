"""API HTTP do servico de IA. Stateless: o Core envia o contexto em cada chamada (ADR-B1-003)."""
import asyncio
import time

from fastapi import FastAPI, HTTPException, Request
from prometheus_client import make_asgi_app
from pydantic import BaseModel, Field

from app.assistente.geracao import gerar
from app.assistente.recuperacao import recuperar
from app.config import config
from app.metricas import LATENCIA, REQUISICOES
from app.modelos import Fonte, PedidoDeRecomendacao, PerguntaAoAssistente, Recomendacoes, RespostaDoAssistente
from app.recomendacao.modelo import MODELO_VERSAO, recomendar

app = FastAPI(title="GameEducator IA", version="0.1.0",
              description="Recomendacao de missoes (ML) e assistente educacional (RAG) do GameEducator.")
app.mount("/metrics", make_asgi_app())

ROTAS_DE_NEGOCIO = {"/recomendacoes", "/assistente/perguntas"}


@app.middleware("http")
async def medir(request: Request, call_next):
    rota = request.url.path
    if rota in ROTAS_DE_NEGOCIO and config.atraso_artificial_ms > 0:
        await asyncio.sleep(config.atraso_artificial_ms / 1000)
    inicio = time.perf_counter()
    resposta = await call_next(request)
    if not rota.startswith("/metrics"):
        LATENCIA.labels(rota).observe(time.perf_counter() - inicio)
        REQUISICOES.labels(rota, str(resposta.status_code)).inc()
    return resposta


@app.get("/saude")
def saude():
    return {"status": "UP", "modeloRecomendacao": MODELO_VERSAO, "provedorLlm": config.llm_provedor}


@app.post("/recomendacoes", response_model=Recomendacoes)
def post_recomendacoes(pedido: PedidoDeRecomendacao) -> Recomendacoes:
    return recomendar(pedido)


@app.post("/assistente/perguntas", response_model=RespostaDoAssistente)
def post_pergunta(pergunta: PerguntaAoAssistente) -> RespostaDoAssistente:
    contexto = recuperar(pergunta.pergunta, pergunta.documentos)
    texto, provedor = gerar(pergunta.pergunta, [doc for doc, _ in contexto])
    fontes = [Fonte(id=doc.id, titulo=doc.titulo, relevancia=score) for doc, score in contexto]
    return RespostaDoAssistente(resposta=texto, fontes=fontes, provedor=provedor)


class Atraso(BaseModel):
    ms: int = Field(ge=0, le=60000)


@app.put("/admin/atraso")
def put_atraso(atraso: Atraso):
    """Lab do Desafio 3: provoca lentidao sem reiniciar o servico. Desligado por padrao."""
    if not config.admin_habilitado:
        raise HTTPException(status_code=404)
    config.atraso_artificial_ms = atraso.ms
    return {"atrasoArtificialMs": config.atraso_artificial_ms}
