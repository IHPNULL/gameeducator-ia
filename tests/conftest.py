import pytest
from fastapi.testclient import TestClient

from app.config import config
from app.main import app


@pytest.fixture
def cliente():
    return TestClient(app)


@pytest.fixture(autouse=True)
def config_padrao():
    original = (config.atraso_artificial_ms, config.admin_habilitado, config.llm_provedor, config.ollama_url)
    yield
    config.atraso_artificial_ms, config.admin_habilitado, config.llm_provedor, config.ollama_url = original
