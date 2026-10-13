"""RF04 - assistente educacional (RAG)."""
import httpx

from app.assistente import geracao
from app.assistente.recuperacao import normalizar, recuperar
from app.config import config
from app.modelos import DocumentoDoCurso

DOCUMENTOS = [
    {"id": "missao-1", "titulo": "Fracoes equivalentes",
     "texto": "Fracoes equivalentes representam a mesma quantidade. Multiplique numerador e denominador pelo mesmo numero."},
    {"id": "missao-2", "titulo": "Porcentagem",
     "texto": "Porcentagem e uma razao de base 100. Para calcular 10% divida por 10."},
]


def test_responde_com_base_no_material_e_cita_as_fontes(cliente):
    resposta = cliente.post("/assistente/perguntas", json={
        "cursoId": 1, "pergunta": "O que sao frações equivalentes?", "documentos": DOCUMENTOS})

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["provedor"] == "extrativo"
    assert corpo["fontes"][0]["id"] == "missao-1"
    assert "mesma quantidade" in corpo["resposta"]


def test_sem_material_relevante_nao_inventa_resposta(cliente):
    resposta = cliente.post("/assistente/perguntas", json={
        "cursoId": 1, "pergunta": "Quem descobriu o Brasil?", "documentos": DOCUMENTOS})

    corpo = resposta.json()
    assert corpo["fontes"] == []
    assert corpo["resposta"] == geracao.SEM_CONTEXTO


def test_pergunta_vazia_e_recusada(cliente):
    resposta = cliente.post("/assistente/perguntas", json={"cursoId": 1, "pergunta": "", "documentos": []})

    assert resposta.status_code == 422


def test_recuperacao_ignora_stopwords_e_documentos_vazios():
    assert normalizar("O que é a Fração?") == ["fracao"]
    assert recuperar("de que", [DocumentoDoCurso(**DOCUMENTOS[0])]) == []
    assert recuperar("fracao", [DocumentoDoCurso(id="x", titulo="", texto="...")]) == []


def test_extrativo_sem_frase_com_termos_da_pergunta():
    doc = DocumentoDoCurso(id="x", titulo="Fracoes", texto="Conteudo sem relacao.")

    assert geracao.extrativo("fracoes", [doc]) == geracao.SEM_CONTEXTO


def test_ollama_e_usado_quando_configurado(monkeypatch):
    config.llm_provedor = "ollama"
    chamadas = []

    def falso_post(url, json, timeout):
        chamadas.append((url, json["model"]))
        return httpx.Response(200, json={"response": " Resposta do LLM "}, request=httpx.Request("POST", url))

    monkeypatch.setattr(geracao.httpx, "post", falso_post)

    texto, provedor = geracao.gerar("fracoes", [DocumentoDoCurso(**DOCUMENTOS[0])])

    assert (texto, provedor) == ("Resposta do LLM", "ollama")
    assert chamadas[0][0].endswith("/api/generate")


def test_llm_indisponivel_degrada_para_extrativo(monkeypatch):
    config.llm_provedor = "ollama"

    def falha(*args, **kwargs):
        raise httpx.ConnectError("sem ollama")

    monkeypatch.setattr(geracao.httpx, "post", falha)

    texto, provedor = geracao.gerar("fracoes equivalentes", [DocumentoDoCurso(**DOCUMENTOS[0])])

    assert provedor == "extrativo"
    assert "mesma quantidade" in texto
