"""Modelo de recomendacao de missoes.

Baseline heuristico e explicavel, versionado em MODELO_VERSAO. O ponto arquitetural do Desafio 3
nao e a qualidade do modelo, e sim a fronteira: este arquivo pode ser substituido por um modelo
treinado (scikit-learn, etc.) com ciclo de deploy proprio, sem tocar no Core Java.
"""
from app.modelos import MissaoParaRecomendar, PedidoDeRecomendacao, Recomendacao, Recomendacoes

MODELO_VERSAO = "baseline-0.1"


def _pontuar(missao: MissaoParaRecomendar) -> tuple[float, str] | None:
    if missao.total_desafios == 0 or missao.desafios_acertados >= missao.total_desafios:
        return None  # missao vazia ou ja concluida: nao recomenda
    progresso = missao.desafios_acertados / missao.total_desafios
    erros = max(missao.tentativas - missao.desafios_acertados, 0)
    dificuldade = erros / missao.tentativas if missao.tentativas else 0.0
    iniciada = missao.tentativas > 0

    pontuacao = 0.5 * iniciada + 0.3 * (1 - progresso) + 0.2 * dificuldade
    if iniciada and dificuldade >= 0.5:
        motivo = "Voce comecou esta missao e errou bastante: vale revisar e terminar"
    elif iniciada:
        motivo = "Voce ja comecou esta missao: falta pouco para concluir"
    else:
        motivo = "Proxima missao ainda nao iniciada"
    return round(pontuacao, 4), motivo


def recomendar(pedido: PedidoDeRecomendacao) -> Recomendacoes:
    pontuadas = []
    for missao in pedido.missoes:
        resultado = _pontuar(missao)
        if resultado is not None:
            pontuacao, motivo = resultado
            pontuadas.append(Recomendacao(missao_id=missao.missao_id, titulo=missao.titulo,
                                          pontuacao=pontuacao, motivo=motivo))
    # maior pontuacao primeiro; empate -> ordem do curso (missao_id)
    pontuadas.sort(key=lambda r: (-r.pontuacao, r.missao_id))
    return Recomendacoes(modelo_versao=MODELO_VERSAO, itens=pontuadas[: pedido.limite])
