def _criar_turma(client, headers, professor_id):
    curso_id = client.post("/cursos/", headers=headers, json={"nome": "Curso Teste", "nivel": "Iniciante"}).get_json()["id"]
    return client.post(
        "/turmas/", headers=headers, json={"nome": "Turma A", "curso_id": curso_id, "professor_id": professor_id}
    ).get_json()["id"]


def _criar_aluno(client, headers, email="aluno@teste.com"):
    return client.post(
        "/alunos/", headers=headers, json={"nome": "Aluno Teste", "email": email, "cpf": "888.888.888-88"}
    ).get_json()["id"]


def test_criar_turma_aluno(client, admin, admin_headers):
    aluno_id = _criar_aluno(client, admin_headers)
    turma_id = _criar_turma(client, admin_headers, admin.id)
    resposta = client.post("/turma-alunos/", headers=admin_headers, json={"aluno_id": aluno_id, "turma_id": turma_id})
    assert resposta.status_code == 201


def test_turma_aluno_duplicado_retorna_409(client, admin, admin_headers):
    aluno_id = _criar_aluno(client, admin_headers)
    turma_id = _criar_turma(client, admin_headers, admin.id)
    dados = {"aluno_id": aluno_id, "turma_id": turma_id}
    client.post("/turma-alunos/", headers=admin_headers, json=dados)
    resposta = client.post("/turma-alunos/", headers=admin_headers, json=dados)
    assert resposta.status_code == 409


def test_criar_turma_aluno_comum_bloqueado(client, admin, admin_headers, comum_headers):
    aluno_id = _criar_aluno(client, admin_headers)
    turma_id = _criar_turma(client, admin_headers, admin.id)
    resposta = client.post("/turma-alunos/", headers=comum_headers, json={"aluno_id": aluno_id, "turma_id": turma_id})
    assert resposta.status_code == 403
