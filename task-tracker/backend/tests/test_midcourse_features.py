from datetime import date, timedelta

PAST_DATE = (date.today() - timedelta(days=1)).isoformat()
FUTURE_DATE = (date.today() + timedelta(days=30)).isoformat()


# --- Due dates + overdue filter -------------------------------------------------


def test_create_task_with_valid_due_date_returns_201(client):
    response = client.post("/tasks", json={"title": "Ship the report", "due_date": FUTURE_DATE})

    assert response.status_code == 201
    body = response.json()
    assert body["due_date"] == FUTURE_DATE
    assert body["is_overdue"] is False


def test_create_task_with_invalid_due_date_format_returns_422(client):
    response = client.post("/tasks", json={"title": "Bad date", "due_date": "not-a-date"})

    assert response.status_code == 422
    assert any("due_date" in str(error.get("loc", [])) for error in response.json()["detail"])


def test_task_with_past_due_date_and_open_status_is_overdue(client):
    create_response = client.post("/tasks", json={"title": "Late task", "due_date": PAST_DATE})

    assert create_response.json()["is_overdue"] is True


def test_task_with_past_due_date_but_done_status_is_not_overdue(client):
    create_response = client.post("/tasks", json={"title": "Finished late", "due_date": PAST_DATE})
    task_id = create_response.json()["id"]

    client.patch(f"/tasks/{task_id}", json={"status": "InProgress"})
    response = client.patch(f"/tasks/{task_id}", json={"status": "Done"})

    assert response.status_code == 200
    assert response.json()["is_overdue"] is False


def test_patch_updates_due_date(client, created_task):
    task_id = created_task["id"]

    response = client.patch(f"/tasks/{task_id}", json={"due_date": FUTURE_DATE})

    assert response.status_code == 200
    assert response.json()["due_date"] == FUTURE_DATE


def test_patch_clears_due_date_with_null(client):
    create_response = client.post("/tasks", json={"title": "Has a due date", "due_date": FUTURE_DATE})
    task_id = create_response.json()["id"]

    response = client.patch(f"/tasks/{task_id}", json={"due_date": None})

    assert response.status_code == 200
    assert response.json()["due_date"] is None


def test_list_tasks_filter_overdue_returns_only_overdue(client):
    client.post("/tasks", json={"title": "Overdue", "due_date": PAST_DATE})
    client.post("/tasks", json={"title": "Not due yet", "due_date": FUTURE_DATE})
    client.post("/tasks", json={"title": "No due date"})

    response = client.get("/tasks", params={"overdue": "true"})

    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    assert titles == ["Overdue"]


def test_list_tasks_filter_overdue_no_match_returns_200_and_empty_list(client):
    client.post("/tasks", json={"title": "Not due yet", "due_date": FUTURE_DATE})

    response = client.get("/tasks", params={"overdue": "true"})

    assert response.status_code == 200
    assert response.json() == []


# --- Tags / labels ---------------------------------------------------------------


def test_create_task_with_tags_returns_201_with_trimmed_tags(client):
    response = client.post("/tasks", json={"title": "Tagged task", "tags": [" backend ", "api"]})

    assert response.status_code == 201
    assert response.json()["tags"] == ["backend", "api"]


def test_create_task_with_blank_tag_returns_422(client):
    response = client.post("/tasks", json={"title": "Blank tag", "tags": ["   "]})

    assert response.status_code == 422
    assert any("tags" in str(error.get("loc", [])) for error in response.json()["detail"])


def test_create_task_with_too_many_tags_returns_422(client):
    response = client.post("/tasks", json={"title": "Too many tags", "tags": [f"tag{i}" for i in range(11)]})

    assert response.status_code == 422


def test_create_task_with_duplicate_tags_deduplicates_case_insensitively(client):
    response = client.post("/tasks", json={"title": "Dup tags", "tags": ["Backend", "backend", "BACKEND"]})

    assert response.status_code == 201
    assert response.json()["tags"] == ["Backend"]


def test_patch_replaces_tags(client):
    create_response = client.post("/tasks", json={"title": "Retag me", "tags": ["old"]})
    task_id = create_response.json()["id"]

    response = client.patch(f"/tasks/{task_id}", json={"tags": ["new", "fresh"]})

    assert response.status_code == 200
    assert response.json()["tags"] == ["new", "fresh"]


def test_patch_omitting_tags_keeps_existing_tags(client):
    create_response = client.post("/tasks", json={"title": "Keep my tags", "tags": ["keep-me"]})
    task_id = create_response.json()["id"]

    response = client.patch(f"/tasks/{task_id}", json={"title": "Keep my tags (renamed)"})

    assert response.status_code == 200
    assert response.json()["tags"] == ["keep-me"]


def test_list_tasks_filter_by_tag_returns_only_matches(client):
    client.post("/tasks", json={"title": "Backend work", "tags": ["backend"]})
    client.post("/tasks", json={"title": "Frontend work", "tags": ["frontend"]})

    response = client.get("/tasks", params={"tag": "backend"})

    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    assert titles == ["Backend work"]


def test_list_tasks_filter_by_tag_no_match_returns_200_and_empty_list(client):
    client.post("/tasks", json={"title": "Backend work", "tags": ["backend"]})

    response = client.get("/tasks", params={"tag": "nonexistent"})

    assert response.status_code == 200
    assert response.json() == []
