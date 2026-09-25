def _criar_aluno(client, headers, email):
    return client.post(
        "/alunos/", headers=headers, json={"nome": "Aluno Teste", "email": email, "cpf": "121.212.121-21"}
    ).get_json()["id"]


def test_comum_consegue_criar_anotacao(client, admin_headers, comum_headers):
    aluno_id = _criar_aluno(client, admin_headers, "anotacao@teste.com")
    resposta = client.post(
        "/anotacoes/", headers=comum_headers,
        json={"aluno_id": aluno_id, "conteudo": "Tem dificuldade com verbos irregulares"},
    )
    assert resposta.status_code == 201


def test_anotacao_registra_quem_escreveu(client, comum, admin_headers, comum_headers):
    aluno_id = _criar_aluno(client, admin_headers, "anotacao2@teste.com")
    resposta = client.post(
        "/anotacoes/", headers=comum_headers, json={"aluno_id": aluno_id, "conteudo": "Observação"}
    )
    assert resposta.get_json()["professor_id"] == comum.id


def test_anotacao_aluno_invalido_retorna_400(client, comum_headers):
    resposta = client.post(
        "/anotacoes/", headers=comum_headers, json={"aluno_id": "id-inexistente", "conteudo": "Observação"}
    )
    assert resposta.status_code == 400
