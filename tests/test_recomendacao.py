"""RF03 - recomendacao de missoes."""

MISSOES = [
    {"missaoId": 1, "titulo": "Fracoes", "totalDesafios": 2, "desafiosAcertados": 2, "tentativas": 2, "xpTotal": 20},
    {"missaoId": 2, "titulo": "Decimais", "totalDesafios": 4, "desafiosAcertados": 1, "tentativas": 5, "xpTotal": 40},
    {"missaoId": 3, "titulo": "Porcentagem", "totalDesafios": 3, "desafiosAcertados": 0, "tentativas": 0, "xpTotal": 30},
    {"missaoId": 4, "titulo": "Vazia", "totalDesafios": 0, "desafiosAcertados": 0, "tentativas": 0, "xpTotal": 0},
    {"missaoId": 5, "titulo": "Quase", "totalDesafios": 4, "desafiosAcertados": 3, "tentativas": 3, "xpTotal": 40},
]


def test_recomenda_iniciadas_primeiro_e_ignora_concluidas(cliente):
    resposta = cliente.post("/recomendacoes", json={"alunoId": 7, "cursoId": 1, "missoes": MISSOES})

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["modeloVersao"] == "baseline-0.1"
    assert [i["missaoId"] for i in corpo["itens"]] == [2, 5, 3]
    assert "errou bastante" in corpo["itens"][0]["motivo"]
    assert "falta pouco" in corpo["itens"][1]["motivo"]
    assert "nao iniciada" in corpo["itens"][2]["motivo"]


def test_respeita_o_limite(cliente):
    resposta = cliente.post("/recomendacoes", json={"alunoId": 7, "cursoId": 1, "missoes": MISSOES, "limite": 1})

    assert [i["missaoId"] for i in resposta.json()["itens"]] == [2]


def test_contrato_invalido_retorna_422(cliente):
    resposta = cliente.post("/recomendacoes", json={"alunoId": 7, "missoes": []})

    assert resposta.status_code == 422
