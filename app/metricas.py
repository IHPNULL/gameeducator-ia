"""Metricas Prometheus do servico de IA (Desafio 6)."""
from prometheus_client import Counter, Histogram

REQUISICOES = Counter("ia_requisicoes_total", "Requisicoes recebidas pelo servico de IA", ["rota", "status"])
LATENCIA = Histogram("ia_latencia_segundos", "Latencia das rotas do servico de IA", ["rota"],
                     buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10))
