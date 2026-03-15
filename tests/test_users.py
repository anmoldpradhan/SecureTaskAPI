def test_create_user(client):
    response = client.post("/users/", json={
        "email": "test@test.com",
        "username": "testuser",
        "password": "password123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@test.com"
    assert data["username"] == "testuser"
    assert "hashed_password" not in data

def test_create_duplicate_user(client):
    client.post("/users/", json={
        "email": "test@test.com",
        "username": "testuser",
        "password": "password123"
    })
    response = client.post("/users/", json={
        "email": "test@test.com",
        "username": "testuser2",
        "password": "password123"
    })
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_get_user(client):
    create = client.post("/users/", json={
        "email": "test@test.com",
        "username": "testuser",
        "password": "password123"
    })
    user_id = create.json()["id"]
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["id"] == user_id

def test_get_nonexistent_user(client):
    response = client.get("/users/9999")
    assert response.status_code == 404