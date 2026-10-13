"""Configuracao por variaveis de ambiente (12-factor): a mesma imagem roda em dev, lab e CI."""
import os
from dataclasses import dataclass


@dataclass
class Config:
    # Atraso artificial (ms) aplicado as rotas de negocio: usado no lab do Desafio 3 para
    # provocar timeout no Core sem derrubar o servico.
    atraso_artificial_ms: int = int(os.getenv("IA_ATRASO_ARTIFICIAL_MS", "0"))
    # Habilita /admin/* (alterar atraso em tempo de execucao). Nunca ligar fora do laboratorio.
    admin_habilitado: bool = os.getenv("IA_ADMIN_HABILITADO", "false").lower() == "true"
    # "extrativo" (padrao, sem dependencia externa) ou "ollama" (LLM local).
    llm_provedor: str = os.getenv("IA_LLM_PROVEDOR", "extrativo")
    ollama_url: str = os.getenv("IA_OLLAMA_URL", "http://localhost:11434")
    ollama_modelo: str = os.getenv("IA_OLLAMA_MODELO", "llama3.2")
    ollama_timeout_s: float = float(os.getenv("IA_OLLAMA_TIMEOUT_S", "20"))


config = Config()
