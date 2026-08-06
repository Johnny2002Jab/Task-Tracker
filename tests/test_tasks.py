from app.models import TaskPriority, TaskStatus


def test_create_task_valid_returns_201_with_full_body(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Write tests",
            "description": "Create pytest coverage",
            "status": "ToDo",
            "priority": "High",
            "assignee": "Alice",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Write tests"
    assert body["description"] == "Create pytest coverage"
    assert body["status"] == TaskStatus.TODO.value
    assert body["priority"] == TaskPriority.HIGH.value
    assert body["assignee"] == "Alice"
    assert body["id"]
    assert body["created_at"]
    assert body["updated_at"]


def test_create_task_missing_title_returns_422(client):
    response = client.post("/tasks", json={"description": "No title"})

    assert response.status_code == 422
    assert response.json()["detail"]


def test_create_task_blank_title_returns_422(client):
    response = client.post("/tasks", json={"title": "   "})

    assert response.status_code == 422
    assert response.json()["detail"]


def test_create_task_invalid_priority_returns_422(client):
    response = client.post("/tasks", json={"title": "Bad priority", "priority": "Urgent"})

    assert response.status_code == 422
    assert response.json()["detail"]


def test_create_task_unknown_field_returns_422(client):
    response = client.post("/tasks", json={"title": "Extra field", "extra": "value"})

    assert response.status_code == 422
    assert response.json()["detail"]


def test_list_tasks_empty_returns_200_and_empty_list(client):
    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_filter_by_status_no_match_returns_200_and_empty_list(client):
    client.post("/tasks", json={"title": "First task"})

    response = client.get("/tasks?status=Done")

    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_filter_by_priority_returns_only_matches(client):
    client.post("/tasks", json={"title": "Low task", "priority": "Low"})
    client.post("/tasks", json={"title": "High task", "priority": "High"})

    response = client.get("/tasks?priority=High")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "High task"
    assert data[0]["priority"] == TaskPriority.HIGH.value


def test_get_task_by_id_returns_task(client, created_task):
    task_id = created_task["id"]

    response = client.get(f"/tasks/{task_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == task_id
    assert body["title"] == "fixture task"
    assert body["status"] == TaskStatus.TODO.value


def test_get_task_by_id_not_found_returns_404_with_detail(client):
    response = client.get("/tasks/not-a-real-id")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task with id not-a-real-id not found"


def test_patch_partial_update_keeps_other_fields(client, created_task):
    task_id = created_task["id"]

    response = client.patch(f"/tasks/{task_id}", json={"title": "Updated title"})

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == task_id
    assert body["title"] == "Updated title"
    assert body["description"] == ""
    assert body["status"] == TaskStatus.TODO.value
    assert body["priority"] == TaskPriority.MEDIUM.value


def test_patch_not_found_returns_404(client):
    response = client.patch("/tasks/not-a-real-id", json={"title": "Nope"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Task with id not-a-real-id not found"


def test_patch_valid_transition_todo_to_inprogress_returns_200(client, created_task):
    task_id = created_task["id"]

    response = client.patch(f"/tasks/{task_id}", json={"status": "InProgress"})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == TaskStatus.IN_PROGRESS.value


def test_patch_invalid_transition_todo_to_done_returns_422(client, created_task):
    task_id = created_task["id"]

    response = client.patch(f"/tasks/{task_id}", json={"status": "Done"})

    assert response.status_code == 422
    assert "Invalid status transition" in response.json()["detail"]


def test_patch_unsupported_priority_returns_422(client):
    create_response = client.post("/tasks", json={"title": "Task with invalid priority"})

    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    response = client.patch(f"/tasks/{task_id}", json={"priority": "Urgent"})

    assert response.status_code == 422
    assert response.json()["detail"]
    assert any("priority" in str(error.get("loc", [])) for error in response.json()["detail"])


def test_patch_inprogress_to_done_returns_200(client):
    create_response = client.post("/tasks", json={"title": "Task to complete"})

    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    client.patch(f"/tasks/{task_id}", json={"status": "InProgress"})
    response = client.patch(f"/tasks/{task_id}", json={"status": "Done"})

    assert response.status_code == 200
    assert response.json()["status"] == "Done"


def test_patch_empty_json_object_returns_422(client):
    create_response = client.post("/tasks", json={"title": "Task with empty patch"})

    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    response = client.patch(f"/tasks/{task_id}", json={})

    assert response.status_code == 422
    assert response.json()["detail"]


def test_patch_same_status_returns_422(client, created_task):
    task_id = created_task["id"]

    response = client.patch(f"/tasks/{task_id}", json={"status": "ToDo"})

    assert response.status_code == 422
    assert "Invalid status transition" in response.json()["detail"]


def test_delete_existing_returns_204_no_body(client, created_task):
    task_id = created_task["id"]

    response = client.delete(f"/tasks/{task_id}")

    assert response.status_code == 204
    assert response.content == b""


def test_delete_missing_returns_404(client):
    response = client.delete("/tasks/not-a-real-id")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task with id not-a-real-id not found"
