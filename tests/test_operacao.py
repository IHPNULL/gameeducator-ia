"""Saude, metricas e injecao de falha do lab."""
import time

from app.config import config


def test_saude(cliente):
    assert cliente.get("/saude").json()["status"] == "UP"


def test_metricas_prometheus_contam_requisicoes(cliente):
    cliente.get("/saude")

    texto = cliente.get("/metrics/").text

    assert 'ia_requisicoes_total{rota="/saude",status="200"}' in texto
    assert "ia_latencia_segundos_bucket" in texto


def test_admin_desligado_por_padrao(cliente):
    assert cliente.put("/admin/atraso", json={"ms": 100}).status_code == 404


def test_atraso_artificial_atrasa_rotas_de_negocio(cliente):
    config.admin_habilitado = True
    assert cliente.put("/admin/atraso", json={"ms": 300}).json() == {"atrasoArtificialMs": 300}

    inicio = time.perf_counter()
    cliente.post("/recomendacoes", json={"alunoId": 1, "cursoId": 1, "missoes": []})

    assert time.perf_counter() - inicio >= 0.3
