def _criar_turma(client, headers, professor_id):
    curso_id = client.post("/cursos/", headers=headers, json={"nome": "Curso Teste", "nivel": "Iniciante"}).get_json()["id"]
    return client.post(
        "/turmas/", headers=headers, json={"nome": "Turma A", "curso_id": curso_id, "professor_id": professor_id}
    ).get_json()["id"]


def test_criar_aula_admin(client, admin, admin_headers):
    turma_id = _criar_turma(client, admin_headers, admin.id)
    resposta = client.post(
        "/aulas/", headers=admin_headers,
        json={"nome": "Aula 1", "data_hora": "2026-10-01T10:00:00", "turma_id": turma_id},
    )
    assert resposta.status_code == 201


def test_criar_aula_comum_bloqueado(client, admin, admin_headers, comum_headers):
    turma_id = _criar_turma(client, admin_headers, admin.id)
    resposta = client.post(
        "/aulas/", headers=comum_headers,
        json={"nome": "Aula 1", "data_hora": "2026-10-01T10:00:00", "turma_id": turma_id},
    )
    assert resposta.status_code == 403


def test_comum_nao_consegue_editar_aula(client, admin, admin_headers, comum_headers):
    turma_id = _criar_turma(client, admin_headers, admin.id)
    criada = client.post(
        "/aulas/", headers=admin_headers,
        json={"nome": "Aula 1", "data_hora": "2026-10-01T10:00:00", "turma_id": turma_id},
    ).get_json()
    resposta = client.put(f"/aulas/{criada['id']}", headers=comum_headers, json={"assunto": "Passado Simples"})
    assert resposta.status_code == 403
