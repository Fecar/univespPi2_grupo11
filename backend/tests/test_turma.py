def _criar_curso(client, headers):
    return client.post("/cursos/", headers=headers, json={"nome": "Curso Teste", "nivel": "Iniciante"}).get_json()["id"]


def test_criar_turma_admin(client, admin, admin_headers):
    curso_id = _criar_curso(client, admin_headers)
    resposta = client.post(
        "/turmas/", headers=admin_headers,
        json={"nome": "Turma A", "curso_id": curso_id, "professor_id": admin.id},
    )
    assert resposta.status_code == 201


def test_criar_turma_comum_bloqueado(client, admin, admin_headers, comum_headers):
    curso_id = _criar_curso(client, admin_headers)
    resposta = client.post(
        "/turmas/", headers=comum_headers,
        json={"nome": "Turma A", "curso_id": curso_id, "professor_id": admin.id},
    )
    assert resposta.status_code == 403


def test_turma_professor_invalido_retorna_400(client, admin_headers):
    curso_id = _criar_curso(client, admin_headers)
    resposta = client.post(
        "/turmas/", headers=admin_headers,
        json={"nome": "Turma A", "curso_id": curso_id, "professor_id": "id-inexistente"},
    )
    assert resposta.status_code == 400


def test_comum_nao_consegue_editar_turma(client, admin, admin_headers, comum_headers):
    curso_id = _criar_curso(client, admin_headers)
    criada = client.post(
        "/turmas/", headers=admin_headers,
        json={"nome": "Turma A", "curso_id": curso_id, "professor_id": admin.id},
    ).get_json()
    resposta = client.put(f"/turmas/{criada['id']}", headers=comum_headers, json={"nome": "Turma A - Manhã"})
    assert resposta.status_code == 403
