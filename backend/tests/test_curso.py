def test_criar_curso_admin(client, admin_headers):
    resposta = client.post(
        "/cursos/", headers=admin_headers, json={"nome": "Inglês Básico", "nivel": "Iniciante"}
    )
    assert resposta.status_code == 201


def test_criar_curso_comum_bloqueado(client, comum_headers):
    resposta = client.post(
        "/cursos/", headers=comum_headers, json={"nome": "Inglês Básico", "nivel": "Iniciante"}
    )
    assert resposta.status_code == 403


def test_criar_curso_sem_nivel_retorna_422(client, admin_headers):
    resposta = client.post("/cursos/", headers=admin_headers, json={"nome": "Inglês Básico"})
    assert resposta.status_code == 422


def test_comum_consegue_ver_curso(client, admin_headers, comum_headers):
    criado = client.post("/cursos/", headers=admin_headers, json={"nome": "Inglês Básico", "nivel": "Iniciante"}).get_json()
    resposta = client.get(f"/cursos/{criado['id']}", headers=comum_headers)
    assert resposta.status_code == 200


def test_comum_nao_consegue_editar_curso(client, admin_headers, comum_headers):
    criado = client.post("/cursos/", headers=admin_headers, json={"nome": "Inglês Básico", "nivel": "Iniciante"}).get_json()
    resposta = client.put(f"/cursos/{criado['id']}", headers=comum_headers, json={"nivel": "Avançado"})
    assert resposta.status_code == 403


def test_comum_nao_consegue_deletar_curso(client, admin_headers, comum_headers):
    criado = client.post(
        "/cursos/", headers=admin_headers, json={"nome": "Inglês Básico", "nivel": "Iniciante"}
    ).get_json()

    resposta = client.delete(f"/cursos/{criado['id']}", headers=comum_headers)
    assert resposta.status_code == 403
