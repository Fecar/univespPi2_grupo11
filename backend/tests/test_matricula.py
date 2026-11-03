def _criar_aluno(client, headers, email="aluno@teste.com"):
    resposta = client.post(
        "/alunos/", headers=headers, json={"nome": "Aluno Teste", "email": email, "cpf": "333.333.333-33"}
    )
    return resposta.get_json()["id"]


def _criar_curso(client, headers):
    resposta = client.post(
        "/cursos/", headers=headers, json={"nome": "Curso Teste", "nivel": "Iniciante"}
    )
    return resposta.get_json()["id"]


def test_criar_matricula(client, admin_headers):
    aluno_id = _criar_aluno(client, admin_headers)
    curso_id = _criar_curso(client, admin_headers)

    resposta = client.post(
        "/matriculas/", headers=admin_headers, json={"aluno_id": aluno_id, "curso_id": curso_id}
    )
    assert resposta.status_code == 201


def test_matricula_duplicada_retorna_409(client, admin_headers):
    aluno_id = _criar_aluno(client, admin_headers)
    curso_id = _criar_curso(client, admin_headers)
    dados = {"aluno_id": aluno_id, "curso_id": curso_id}

    client.post("/matriculas/", headers=admin_headers, json=dados)
    resposta = client.post("/matriculas/", headers=admin_headers, json=dados)
    assert resposta.status_code == 409


def test_matricula_aluno_invalido_retorna_400(client, admin_headers):
    curso_id = _criar_curso(client, admin_headers)
    resposta = client.post(
        "/matriculas/", headers=admin_headers, json={"aluno_id": "id-inexistente", "curso_id": curso_id}
    )
    assert resposta.status_code == 400
