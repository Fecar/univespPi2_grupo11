def test_criar_aluno_admin(client, admin_headers):
    resposta = client.post(
        "/alunos/", headers=admin_headers,
        json={"nome": "Aluno Teste", "email": "aluno@teste.com", "cpf": "444.444.444-44"},
    )
    assert resposta.status_code == 201


def test_criar_aluno_comum_bloqueado(client, comum_headers):
    resposta = client.post(
        "/alunos/", headers=comum_headers,
        json={"nome": "Aluno Teste", "email": "aluno2@teste.com", "cpf": "555.555.555-55"},
    )
    assert resposta.status_code == 403


def test_comum_consegue_ver_aluno(client, admin_headers, comum_headers):
    criado = client.post(
        "/alunos/", headers=admin_headers,
        json={"nome": "Aluno Teste", "email": "aluno3@teste.com", "cpf": "666.666.666-66"},
    ).get_json()
    resposta = client.get(f"/alunos/{criado['id']}", headers=comum_headers)
    assert resposta.status_code == 200


def test_comum_nao_consegue_editar_aluno(client, admin_headers, comum_headers):
    criado = client.post(
        "/alunos/", headers=admin_headers,
        json={"nome": "Aluno Teste 1", "email": "aluno4@teste.com", "cpf": "777.777.777-77"},
    ).get_json()
    resposta = client.put(f"/alunos/{criado['id']}", headers=comum_headers, json={"nome": "Aluno Teste 2"})
    assert resposta.status_code == 403
