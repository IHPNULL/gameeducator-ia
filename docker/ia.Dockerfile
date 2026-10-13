# Build context: raiz do repositorio gameeducator-ia
# Mesmo padrao dos outros repos (ADR-016 da AC1): deps -> test -> runtime.
#   test    -> roda pytest + gate de cobertura (90%). A pipeline builda --target test e roda com
#              "docker run" para extrair reports/ mesmo quando um teste falha.
#   runtime -> so o codigo da aplicacao + dependencias de producao.

FROM python:3.12-slim AS deps
WORKDIR /app
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_NO_CACHE_DIR=1 PYTHONDONTWRITEBYTECODE=1
COPY requirements.txt ./
RUN pip install -r requirements.txt

FROM deps AS test
COPY requirements-dev.txt pytest.ini ./
RUN pip install -r requirements-dev.txt
COPY app/ app/
COPY tests/ tests/
CMD ["python", "-m", "pytest"]

FROM deps AS runtime
COPY app/ app/
RUN useradd --create-home ia
USER ia
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/saude', timeout=2)"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
