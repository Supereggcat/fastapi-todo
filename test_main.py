import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from database import Base, get_db

TEST_DATABASE_URL = "sqlite:///./test_todos.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture
def user_token():
    """创建用户并返回 JWT Token"""
    username = "testuser"
    password = "testpass123"
    resp = client.post("/register", json={"username": username, "password": password})
    print(f"\n[DEBUG] Register status: {resp.status_code}")
    resp2 = client.post("/login", data={"username": username, "password": password})
    print(f"[DEBUG] Login status: {resp2.status_code}")
    print(f"[DEBUG] Login response: {resp2.json()}")
    return resp2.json()["access_token"]


# --------------------------------------------------
# 调试测试：先确认 Token 是否能通过鉴权
# --------------------------------------------------

def test_health():
    """确认 API 能正常注册和登录"""
    resp = client.post("/register", json={"username": "admin", "password": "admin123"})
    assert resp.status_code == 201

    resp2 = client.post("/login", data={"username": "admin", "password": "admin123"})
    assert resp2.status_code == 200
    token = resp2.json()["access_token"]
    assert token is not None

    # 用 Token 访问 /me
    resp3 = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert resp3.status_code == 200, f"/me failed: {resp3.json()}"
    assert resp3.json()["username"] == "admin"


def test_todo_with_token(user_token):
    """确认带 Token 能访问 todo 接口"""
    print(f"[DEBUG] Token: {user_token[:20]}...")
    resp = client.post("/todos", json={"title": "测一下"}, headers={"Authorization": f"Bearer {user_token}"})
    print(f"[DEBUG] Create todo status: {resp.status_code}")
    print(f"[DEBUG] Create todo body: {resp.json()}")
    assert resp.status_code == 201


# --------------------------------------------------
# 用户认证测试
# --------------------------------------------------

class TestAuth:
    def test_register_success(self):
        response = client.post("/register", json={
            "username": "newuser",
            "password": "password123",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert "id" in data
        assert "password" not in data

    def test_register_duplicate_username(self):
        client.post("/register", json={"username": "dupuser", "password": "password123"})
        response = client.post("/register", json={"username": "dupuser", "password": "password123"})
        assert response.status_code == 400
        assert "已存在" in response.json()["detail"]

    def test_login_success(self):
        client.post("/register", json={"username": "logintest", "password": "password123"})
        response = client.post("/login", data={"username": "logintest", "password": "password123"})
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self):
        client.post("/register", json={"username": "wrongpwd", "password": "password123"})
        response = client.post("/login", data={"username": "wrongpwd", "password": "wrongpass"})
        assert response.status_code == 401

    def test_me_without_token(self):
        response = client.get("/me")
        assert response.status_code == 401


# --------------------------------------------------
# Todo CRUD 测试
# --------------------------------------------------

class TestTodos:
    def test_create_todo(self, user_token):
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.post("/todos", json={
            "title": "学习 FastAPI",
        }, headers=headers)
        assert response.status_code == 201, f"Got {response.status_code}: {response.json()}"
        data = response.json()
        assert data["title"] == "学习 FastAPI"
        assert data["completed"] is False
        assert "id" in data

    def test_list_todos(self, user_token):
        headers = {"Authorization": f"Bearer {user_token}"}
        client.post("/todos", json={"title": "任务1"}, headers=headers)
        client.post("/todos", json={"title": "任务2"}, headers=headers)
        response = client.get("/todos", headers=headers)
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_get_single_todo(self, user_token):
        headers = {"Authorization": f"Bearer {user_token}"}
        create_resp = client.post("/todos", json={"title": "单条查询"}, headers=headers)
        todo_id = create_resp.json()["id"]
        response = client.get(f"/todos/{todo_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["title"] == "单条查询"

    def test_update_todo(self, user_token):
        headers = {"Authorization": f"Bearer {user_token}"}
        create_resp = client.post("/todos", json={"title": "原标题"}, headers=headers)
        todo_id = create_resp.json()["id"]
        response = client.put(f"/todos/{todo_id}", json={
            "title": "新标题",
            "completed": True,
        }, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "新标题"
        assert data["completed"] is True

    def test_delete_todo(self, user_token):
        headers = {"Authorization": f"Bearer {user_token}"}
        create_resp = client.post("/todos", json={"title": "待删除"}, headers=headers)
        todo_id = create_resp.json()["id"]
        response = client.delete(f"/todos/{todo_id}", headers=headers)
        assert response.status_code == 204

    def test_other_user_cannot_access(self, user_token):
        headers = {"Authorization": f"Bearer {user_token}"}
        create_resp = client.post("/todos", json={"title": "A的秘密"}, headers=headers)
        todo_id = create_resp.json()["id"]

        client.post("/register", json={"username": "userb", "password": "password123"})
        b_resp = client.post("/login", data={"username": "userb", "password": "password123"})
        b_token = b_resp.json()["access_token"]
        response = client.get(f"/todos/{todo_id}", headers={"Authorization": f"Bearer {b_token}"})
        assert response.status_code == 404

    def test_create_todo_without_auth(self):
        response = client.post("/todos", json={"title": "无权限"})
        assert response.status_code == 401