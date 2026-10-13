"""Contrato HTTP do servico (JSON em camelCase, igual aos records do Core Java)."""
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class Base(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class MissaoParaRecomendar(Base):
    missao_id: int
    titulo: str
    total_desafios: int = Field(ge=0)
    desafios_acertados: int = Field(ge=0)
    tentativas: int = Field(ge=0)
    xp_total: int = Field(ge=0)


class PedidoDeRecomendacao(Base):
    aluno_id: int
    curso_id: int
    missoes: list[MissaoParaRecomendar]
    limite: int = Field(default=3, ge=1, le=20)


class Recomendacao(Base):
    missao_id: int
    titulo: str
    pontuacao: float
    motivo: str


class Recomendacoes(Base):
    modelo_versao: str
    itens: list[Recomendacao]


class DocumentoDoCurso(Base):
    id: str
    titulo: str
    texto: str


class PerguntaAoAssistente(Base):
    curso_id: int
    pergunta: str = Field(min_length=1, max_length=500)
    documentos: list[DocumentoDoCurso]


class Fonte(Base):
    id: str
    titulo: str
    relevancia: float


class RespostaDoAssistente(Base):
    resposta: str
    fontes: list[Fonte]
    provedor: str
