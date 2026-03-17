
# ── Helpers ──────────────────────────────────────────────────────────────────
def test_debug_login(client):
    # Step 1 - create user
    create_response = client.post("/users/", json={
        "email": "debug@test.com",
        "username": "debuguser",
        "password": "password123"
    })
    print("\nCreate response:", create_response.status_code, create_response.json())

    # Step 2 - login
    login_response = client.post("/auth/login", data={
        "username": "debug@test.com",
        "password": "password123"
    })
    print("Login response:", login_response.status_code, login_response.json())

def create_user_and_login(client, email="user@test.com", username="testuser", role="user"):
    client.post("/users/", json={
        "email": email,
        "username": username,
        "password": "password123"
    })
    response = client.post("/auth/login", data={
        "username": email,
        "password": "password123"
    })
    return response.json()["access_token"]

def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}

def create_task(client, token, title="Test Task", status="todo", priority=1):
    return client.post("/tasks/", json={
        "title": title,
        "description": "A test task",
        "status": status,
        "priority": priority
    }, headers=auth_headers(token))


# ── Create Task ───────────────────────────────────────────────────────────────

def test_create_task_success(client):
    token = create_user_and_login(client)
    response = create_task(client, token, title="My First Task")
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My First Task"
    assert data["status"] == "todo"
    assert data["priority"] == 1
    assert "owner_id" in data

def test_create_task_unauthenticated(client):
    response = client.post("/tasks/", json={
        "title": "Sneaky Task",
        "status": "todo",
        "priority": 1
    })
    assert response.status_code == 401

def test_create_task_invalid_status(client):
    token = create_user_and_login(client)
    response = client.post("/tasks/", json={
        "title": "Bad Task",
        "status": "invalid_status",
        "priority": 1
    }, headers=auth_headers(token))
    assert response.status_code == 422


# ── Get Tasks ─────────────────────────────────────────────────────────────────

def test_get_own_tasks(client):
    token = create_user_and_login(client)
    create_task(client, token, title="Task 1")
    create_task(client, token, title="Task 2")
    response = client.get("/tasks/", headers=auth_headers(token))
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_get_tasks_empty(client):
    token = create_user_and_login(client)
    response = client.get("/tasks/", headers=auth_headers(token))
    assert response.status_code == 200
    assert response.json() == []

def test_get_tasks_unauthenticated(client):
    response = client.get("/tasks/")
    assert response.status_code == 401

def test_get_specific_task(client):
    token = create_user_and_login(client)
    created = create_task(client, token, title="Specific Task")
    task_id = created.json()["id"]
    response = client.get(f"/tasks/{task_id}", headers=auth_headers(token))
    assert response.status_code == 200
    assert response.json()["title"] == "Specific Task"

def test_get_nonexistent_task(client):
    token = create_user_and_login(client)
    response = client.get("/tasks/9999", headers=auth_headers(token))
    assert response.status_code == 404


# ── Ownership Enforcement ─────────────────────────────────────────────────────

def test_user_cannot_see_other_users_task(client):
    token_a = create_user_and_login(client, "a@test.com", "usera")
    token_b = create_user_and_login(client, "b@test.com", "userb")

    task = create_task(client, token_a, title="User A Task")
    task_id = task.json()["id"]

    response = client.get(f"/tasks/{task_id}", headers=auth_headers(token_b))
    assert response.status_code == 403

def test_user_cannot_update_other_users_task(client):
    token_a = create_user_and_login(client, "a@test.com", "usera")
    token_b = create_user_and_login(client, "b@test.com", "userb")

    task = create_task(client, token_a, title="User A Task")
    task_id = task.json()["id"]

    response = client.put(f"/tasks/{task_id}", json={
        "title": "Hijacked"
    }, headers=auth_headers(token_b))
    assert response.status_code == 403

def test_user_cannot_delete_other_users_task(client):
    token_a = create_user_and_login(client, "a@test.com", "usera")
    token_b = create_user_and_login(client, "b@test.com", "userb")

    task = create_task(client, token_a, title="User A Task")
    task_id = task.json()["id"]

    response = client.delete(f"/tasks/{task_id}", headers=auth_headers(token_b))
    assert response.status_code == 403


# ── Update Task ───────────────────────────────────────────────────────────────

def test_update_task_status(client):
    token = create_user_and_login(client)
    task = create_task(client, token, title="Update Me")
    task_id = task.json()["id"]

    response = client.put(f"/tasks/{task_id}", json={
        "status": "in_progress"
    }, headers=auth_headers(token))
    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"
    assert response.json()["title"] == "Update Me"

def test_update_task_partial(client):
    token = create_user_and_login(client)
    task = create_task(client, token, title="Partial Update", priority=1)
    task_id = task.json()["id"]

    response = client.put(f"/tasks/{task_id}", json={
        "priority": 3
    }, headers=auth_headers(token))
    assert response.status_code == 200
    data = response.json()
    assert data["priority"] == 3
    assert data["title"] == "Partial Update"

def test_update_nonexistent_task(client):
    token = create_user_and_login(client)
    response = client.put("/tasks/9999", json={
        "title": "Ghost Task"
    }, headers=auth_headers(token))
    assert response.status_code == 404


# ── Delete Task ───────────────────────────────────────────────────────────────

def test_delete_task_success(client):
    token = create_user_and_login(client)
    task = create_task(client, token, title="Delete Me")
    task_id = task.json()["id"]

    response = client.delete(f"/tasks/{task_id}", headers=auth_headers(token))
    assert response.status_code == 204

    fetch = client.get(f"/tasks/{task_id}", headers=auth_headers(token))
    assert fetch.status_code == 404

def test_delete_nonexistent_task(client):
    token = create_user_and_login(client)
    response = client.delete("/tasks/9999", headers=auth_headers(token))
    assert response.status_code == 404


# ── Admin RBAC ────────────────────────────────────────────────────────────────

def test_regular_user_cannot_list_all_users(client):
    token = create_user_and_login(client)
    response = client.get("/users", headers=auth_headers(token))
    assert response.status_code == 401

def test_unauthenticated_cannot_list_users(client):
    response = client.get("/users/")
    assert response.status_code == 401