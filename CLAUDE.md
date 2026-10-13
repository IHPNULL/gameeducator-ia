# CLAUDE.md

Servico de IA do GameEducator (Python 3.12, FastAPI). Codigo, comentarios e identificadores em portugues sem acentos.

- `app/main.py` rotas; `app/modelos.py` contrato JSON (camelCase via alias - mantenha igual aos records em
  `gameeducator-backend/.../ia/`); `app/recomendacao/` (RF03); `app/assistente/` (RF04, RAG).
- Testes: `.venv/bin/python -m pytest` (gate 90% em `pytest.ini`). Um teste: `.venv/bin/python -m pytest tests/test_assistente.py -k nome`.
- Mudou o contrato? Atualize os records do Core, `ClienteHttpIaTest` e o smoke do `Jenkinsfile` juntos.
- Stateless por decisao (ADR-B1-003): nao acessar o banco do Core.
