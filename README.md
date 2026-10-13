# GameEducator - Servico de IA

Servico Python (FastAPI) com as capacidades de IA do GameEducator, separado do Core Java por decisao
arquitetural (ADR-B1-003 em `gameeducator-backend/docs/adr/`):

- **RF03 - Recomendacao inteligente** (`POST /recomendacoes`): ordena as proximas missoes do aluno.
  Modelo baseline versionado (`modeloVersao`), substituivel por um modelo treinado sem tocar no Core.
- **RF04 - Assistente educacional / RAG** (`POST /assistente/perguntas`): recupera (TF-IDF) os trechos do
  material do curso enviados pelo Core e gera a resposta (extrativa por padrao; LLM local via Ollama opcional).

O servico e **stateless**: nao acessa o banco do Core; o Core envia o contexto em cada chamada.
Se este servico cair, o Core continua funcionando (recomendacao local e 503 so no assistente).

**Stack:** Python 3.12 · FastAPI · Pydantic 2 · prometheus-client · pytest

**Integrantes (Grupo 6):** Italo Haas Pascoli (190294) · Maria Eduarda Mota Zandonade (200953)

## Como rodar

```bash
python3.12 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m pytest                          # testes + gate de cobertura (90%)
.venv/bin/uvicorn app.main:app --port 8000          # http://localhost:8000/docs
docker build -f docker/ia.Dockerfile -t gameeducator-ia .   # imagem de runtime
```

| Variavel | Padrao | Uso |
|---|---|---|
| `IA_LLM_PROVEDOR` | `extrativo` | `ollama` usa um LLM local (`IA_OLLAMA_URL`, `IA_OLLAMA_MODELO`); se falhar, cai no extrativo |
| `IA_ATRASO_ARTIFICIAL_MS` | `0` | lab: atrasa as rotas de negocio para provocar timeout no Core |
| `IA_ADMIN_HABILITADO` | `false` | lab: habilita `PUT /admin/atraso` (nunca fora do laboratorio) |

Metricas Prometheus em `/metrics` (`ia_requisicoes_total`, `ia_latencia_segundos`). Saude em `/saude`.

## Contrato

JSON em camelCase, espelhado nos records do Core (`org.facens.grupo_6_gameeducator.ia`). Exemplo:

```bash
curl -s localhost:8000/recomendacoes -H 'Content-Type: application/json' -d '{"alunoId":1,"cursoId":1,
  "missoes":[{"missaoId":1,"titulo":"Fracoes","totalDesafios":2,"desafiosAcertados":1,"tentativas":3,"xpTotal":20}]}'
```

## CI

`Jenkinsfile` proprio (pipeline independente do Core): testes na imagem, imagem de runtime e smoke do contrato.
O job `gameeducator-ia` e criado pelo Jenkins local do `gameeducator-backend/jenkins`.
