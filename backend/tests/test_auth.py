def test_login_sucesso(client, admin):
    resposta = client.post(
        "auth/login", json={"email": admin.email, "senha": "senha1234"}
    )
    assert resposta.status_code == 200
    assert "access_token" in resposta.get_json()


def test_login_senha_errada(client, admin):
    resposta = client.post(
        "auth/login", json={"email": admin.email, "senha": "senha-errada"}
    )
    assert resposta.status_code == 401


def test_login_email_inexistente(client):
    resposta = client.post(
        "auth/login", json={"email": "nobody@teste.com", "senha": "senha-qualquer"}
    )
    assert resposta.status_code == 401


def test_login_bloqueia_apos_5_tentativas(client, admin):
    for _ in range(5):
        client.post("auth/login", json={"email": admin.email, "senha": "senha-errada"})

    resposta = client.post(
        "auth/login", json={"email": admin.email, "senha": "senha1234"}
    )
    assert resposta.status_code == 401
    assert "bloqueada" in resposta.get_json()["message"].lower()


def test_login_sem_senha_retorna_422(client, admin):
    resposta = client.post("/auth/login", json={"email": admin.email})
    assert resposta.status_code == 422
