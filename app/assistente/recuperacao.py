"""Recuperacao (o "R" do RAG): TF-IDF + cosseno sobre o material do curso enviado pelo Core.

Sem dependencias pesadas de proposito: o lab precisa subir em segundos. A troca por embeddings +
banco vetorial fica atras desta funcao.
"""
import math
import re
import unicodedata
from collections import Counter

from app.modelos import DocumentoDoCurso

STOPWORDS = set("""
a o as os um uma uns umas de do da dos das em no na nos nas por para com sem que e ou se ao aos
como qual quais quando onde porque por que eh e sao ser foi era isso esse essa este esta isto mais
menos muito pouco me te lhe nos vos the of what is
""".split())


def normalizar(texto: str) -> list[str]:
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    return [t for t in re.findall(r"[a-z0-9/]+", sem_acento) if t not in STOPWORDS and len(t) > 1]


def recuperar(pergunta: str, documentos: list[DocumentoDoCurso], k: int = 3) -> list[tuple[DocumentoDoCurso, float]]:
    termos_pergunta = normalizar(pergunta)
    if not termos_pergunta or not documentos:
        return []
    tokens_docs = [normalizar(d.titulo + " " + d.texto) for d in documentos]
    n = len(documentos)
    df = Counter(t for tokens in tokens_docs for t in set(tokens))
    idf = {t: math.log((1 + n) / (1 + df[t])) + 1 for t in df}

    def vetor(tokens):
        tf = Counter(tokens)
        return {t: tf[t] * idf.get(t, 0.0) for t in tf}

    vq = vetor(termos_pergunta)
    norma_q = math.sqrt(sum(v * v for v in vq.values()))
    if not norma_q:
        return []  # nenhum termo da pergunta aparece no material: nada a recuperar
    resultados = []
    for documento, tokens in zip(documentos, tokens_docs):
        vd = vetor(tokens)
        norma_d = math.sqrt(sum(v * v for v in vd.values()))
        if not norma_d:
            continue
        cosseno = sum(vq[t] * vd.get(t, 0.0) for t in vq) / (norma_q * norma_d)
        if cosseno > 0:
            resultados.append((documento, round(cosseno, 4)))
    resultados.sort(key=lambda par: -par[1])
    return resultados[:k]
