def create_test_user(client):
    client.post("/users/", json={
        "email": "auth@test.com",
        "username": "authuser",
        "password": "password123"
    })

def test_login_success(client):
    create_test_user(client)
    response = client.post("/auth/login", data={
        "username": "auth@test.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client):
    create_test_user(client)
    response = client.post("/auth/login", data={
        "username": "auth@test.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_login_nonexistent_user(client):
    response = client.post("/auth/login", data={
        "username": "nobody@test.com",
        "password": "password123"
    })
    assert response.status_code == 401

def test_protected_route_without_token(client):
    response = client.get("/users/me")
    assert response.status_code == 401

def test_protected_route_with_token(client):
    create_test_user(client)
    login = client.post("/auth/login", data={
        "username": "auth@test.com",
        "password": "password123"
    })
    token = login.json()["access_token"]
    response = client.get("/users/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    assert response.json()["email"] == "auth@test.com"