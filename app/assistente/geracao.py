"""Geracao (o "G" do RAG). Dois provedores atras da mesma funcao:

- "extrativo" (padrao): monta a resposta com as frases do material mais proximas da pergunta.
  Deterministico, sem custo e sem dependencia externa - e o que roda no CI e no lab.
- "ollama": LLM local via HTTP (opcional). Se o LLM falhar, cai no extrativo (degradacao interna).
"""
import logging

import httpx

from app.assistente.recuperacao import normalizar
from app.config import config
from app.modelos import DocumentoDoCurso

log = logging.getLogger(__name__)
SEM_CONTEXTO = "Nao encontrei esse assunto no material do curso. Pergunte ao professor ou reformule a pergunta."


def _frases(texto: str) -> list[str]:
    return [f.strip() for f in texto.replace("?", "?.").split(".") if f.strip()]


def extrativo(pergunta: str, contexto: list[DocumentoDoCurso]) -> str:
    if not contexto:
        return SEM_CONTEXTO
    termos = set(normalizar(pergunta))
    candidatas = []
    for documento in contexto:
        for frase in _frases(documento.texto):
            comuns = len(termos & set(normalizar(frase)))
            if comuns:
                candidatas.append((comuns, documento.titulo, frase))
    if not candidatas:
        return SEM_CONTEXTO
    candidatas.sort(key=lambda c: -c[0])
    trechos = [f"{frase} (fonte: {titulo})" for _, titulo, frase in candidatas[:2]]
    return "Com base no material do curso: " + " ".join(trechos)


def ollama(pergunta: str, contexto: list[DocumentoDoCurso]) -> str:
    material = "\n\n".join(f"[{d.titulo}]\n{d.texto}" for d in contexto)
    prompt = ("Voce e um assistente educacional. Responda em portugues, em ate 3 frases, usando SOMENTE "
              f"o material abaixo. Se nao estiver no material, diga que nao sabe.\n\nMaterial:\n{material}\n\n"
              f"Pergunta: {pergunta}")
    resposta = httpx.post(f"{config.ollama_url}/api/generate",
                          json={"model": config.ollama_modelo, "prompt": prompt, "stream": False},
                          timeout=config.ollama_timeout_s)
    resposta.raise_for_status()
    return resposta.json()["response"].strip()


def gerar(pergunta: str, contexto: list[DocumentoDoCurso]) -> tuple[str, str]:
    """Devolve (resposta, provedor efetivamente usado)."""
    if config.llm_provedor == "ollama" and contexto:
        try:
            return ollama(pergunta, contexto), "ollama"
        except (httpx.HTTPError, KeyError, ValueError) as erro:
            log.warning("LLM indisponivel (%s); usando resposta extrativa", erro)
    return extrativo(pergunta, contexto), "extrativo"
