def test_listar_professores_exige_login(client):
    resposta = client.get("/professores/")
    assert resposta.status_code == 401


def test_obter_professor_proprio_perfil(client, comum, comum_headers):
    resposta = client.get(f"/professores/{comum.id}", headers=comum_headers)
    assert resposta.status_code == 200


def test_obter_perfil_de_outro_professor_bloqueado(client, comum_headers, admin):
    resposta = client.get(f"/professores/{admin.id}", headers=comum_headers)
    assert resposta.status_code == 403


def test_criar_professor_admin_sucesso(client, admin_headers):
    resposta = client.post(
        "/professores/",
        headers=admin_headers,
        json={
            "nome": "Novo Professor 1",
            "email": "novo.prof.1@teste.com",
            "cpf": "111.111.111-11",
            "senha": "senha123",
        },
    )
    assert resposta.status_code == 201


def test_criar_professor_comum_bloqueado(client, comum_headers):
    resposta = client.post(
        "/professores/",
        headers=comum_headers,
        json={
            "nome": "Novo Professor 2",
            "email": "novo.prof.2@teste.com",
            "cpf": "222.222.222-22",
            "senha": "senha123",
        },
    )
    assert resposta.status_code == 403


def test_admin_nao_altera_proprio_privilegio(client, admin, admin_headers):
    resposta = client.put(
        f"/professores/{admin.id}", headers=admin_headers, json={"privilegio": "comum"}
    )
    assert resposta.status_code == 400


def test_admin_nao_consegue_autodeletar(client, admin, admin_headers):
    resposta = client.delete(f"/professores/{admin.id}", headers=admin_headers)
    assert resposta.status_code == 400


def test_admin_consegue_deletar_outro_professor(client, admin_headers, comum):
    resposta = client.delete(f"/professores/{comum.id}", headers=admin_headers)
    assert resposta.status_code == 204
