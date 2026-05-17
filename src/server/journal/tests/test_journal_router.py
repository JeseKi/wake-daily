# -*- coding: utf-8 -*-
from http import HTTPStatus

from src.server.auth import service as auth_service


def _login_admin(test_client):
    resp = test_client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert resp.status_code == HTTPStatus.OK, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def _register_and_login(test_client, username: str):
    email = f"{username}@example.com"
    resp = test_client.post("/api/auth/send-verification-code", json={"email": email})
    assert resp.status_code == HTTPStatus.OK, resp.text
    code = auth_service.verification_codes[email]["code"]
    resp = test_client.post(
        "/api/auth/register-with-code",
        json={
            "username": username,
            "email": email,
            "password": "Password123",
            "code": code,
        },
    )
    assert resp.status_code == HTTPStatus.CREATED, resp.text
    resp = test_client.post(
        "/api/auth/login",
        json={"username": username, "password": "Password123"},
    )
    assert resp.status_code == HTTPStatus.OK, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def test_journal_user_flow(test_client, init_test_database):
    headers = _register_and_login(test_client, "journal_router_user")

    question_resp = test_client.get("/api/journal/today-question", headers=headers)
    assert question_resp.status_code == HTTPStatus.OK, question_resp.text
    question = question_resp.json()

    create_resp = test_client.post(
        "/api/journal/entries",
        headers=headers,
        json={
            "question_id": question["id"],
            "content": "今天我应该慢一点，也不能一直逼自己。",
        },
    )
    assert create_resp.status_code == HTTPStatus.CREATED, create_resp.text
    entry = create_resp.json()
    assert entry["question_content"] == question["content"]
    assert [item["word"] for item in entry["attachment_matches"]] == ["应该", "不能"]

    relief_resp = test_client.post(
        f"/api/journal/entries/{entry['id']}/relief",
        headers=headers,
    )
    repeat_relief_resp = test_client.post(
        f"/api/journal/entries/{entry['id']}/relief",
        headers=headers,
    )
    assert relief_resp.status_code == HTTPStatus.OK, relief_resp.text
    assert repeat_relief_resp.status_code == HTTPStatus.OK, repeat_relief_resp.text
    assert repeat_relief_resp.json()["relief_count"] == 1

    recent_resp = test_client.get(
        "/api/journal/entries/recent?days=7",
        headers=headers,
    )
    assert recent_resp.status_code == HTTPStatus.OK, recent_resp.text
    recent = recent_resp.json()
    assert len(recent) == 1
    assert recent[0]["id"] == entry["id"]
    assert recent[0]["relief_count"] == 1
    assert recent[0]["has_relief_feedback"] is True


def test_journal_requires_authentication(test_client):
    resp = test_client.get("/api/journal/today-question")
    assert resp.status_code == HTTPStatus.UNAUTHORIZED

    resp = test_client.post(
        "/api/journal/entries",
        json={"question_id": 1, "content": "hello"},
    )
    assert resp.status_code == HTTPStatus.UNAUTHORIZED


def test_admin_question_management(test_client, init_test_database):
    admin_headers = _login_admin(test_client)

    create_resp = test_client.post(
        "/api/admin/journal/questions",
        headers=admin_headers,
        json={"content": "管理员新增的问题", "is_active": True, "sort_order": 999},
    )
    assert create_resp.status_code == HTTPStatus.CREATED, create_resp.text
    question = create_resp.json()

    list_resp = test_client.get(
        "/api/admin/journal/questions",
        headers=admin_headers,
    )
    assert list_resp.status_code == HTTPStatus.OK, list_resp.text
    assert any(item["id"] == question["id"] for item in list_resp.json())

    update_resp = test_client.patch(
        f"/api/admin/journal/questions/{question['id']}",
        headers=admin_headers,
        json={"content": "更新后的问题", "is_active": False},
    )
    assert update_resp.status_code == HTTPStatus.OK, update_resp.text
    assert update_resp.json()["content"] == "更新后的问题"
    assert update_resp.json()["is_active"] is False

    delete_resp = test_client.delete(
        f"/api/admin/journal/questions/{question['id']}",
        headers=admin_headers,
    )
    assert delete_resp.status_code == HTTPStatus.NO_CONTENT, delete_resp.text


def test_normal_user_cannot_manage_questions(test_client, init_test_database):
    headers = _register_and_login(test_client, "normal_journal_user")

    resp = test_client.get("/api/admin/journal/questions", headers=headers)
    assert resp.status_code == HTTPStatus.FORBIDDEN

