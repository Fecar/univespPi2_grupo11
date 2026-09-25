def _criar_aula(client, headers, professor_id):
    curso_id = client.post("/cursos/", headers=headers, json={"nome": "Curso Teste", "nivel": "Iniciante"}).get_json()["id"]
    turma_id = client.post(
        "/turmas/", headers=headers, json={"nome": "Turma A", "curso_id": curso_id, "professor_id": professor_id}
    ).get_json()["id"]
    return client.post(
        "/aulas/", headers=headers, json={"nome": "Aula 1", "data_hora": "2026-10-01T10:00:00", "turma_id": turma_id}
    ).get_json()["id"]


def _criar_aluno(client, headers, email="aluno@teste.com"):
    return client.post(
        "/alunos/", headers=headers, json={"nome": "Aluno Teste", "email": email, "cpf": "999.999.999-99"}
    ).get_json()["id"]


def test_comum_consegue_lancar_nota(client, admin, admin_headers, comum_headers):
    aula_id = _criar_aula(client, admin_headers, admin.id)
    aluno_id = _criar_aluno(client, admin_headers)
    resposta = client.post(
        "/avaliacoes/", headers=comum_headers, json={"aluno_id": aluno_id, "aula_id": aula_id, "nota": 8.5}
    )
    assert resposta.status_code == 201


def test_avaliacao_sem_nota_fica_null(client, admin, admin_headers):
    aula_id = _criar_aula(client, admin_headers, admin.id)
    aluno_id = _criar_aluno(client, admin_headers)
    resposta = client.post("/avaliacoes/", headers=admin_headers, json={"aluno_id": aluno_id, "aula_id": aula_id})
    assert resposta.status_code == 201
    assert resposta.get_json()["nota"] is None


def test_avaliacao_duplicada_retorna_409(client, admin, admin_headers):
    aula_id = _criar_aula(client, admin_headers, admin.id)
    aluno_id = _criar_aluno(client, admin_headers)
    dados = {"aluno_id": aluno_id, "aula_id": aula_id, "nota": 7}
    client.post("/avaliacoes/", headers=admin_headers, json=dados)
    resposta = client.post("/avaliacoes/", headers=admin_headers, json=dados)
    assert resposta.status_code == 409
