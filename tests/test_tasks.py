import pytest
from httpx import AsyncClient
import pytest_asyncio

pytestmark = pytest.mark.asyncio

@pytest_asyncio.fixture
async def auth_client(async_client: AsyncClient):
    # Register and login to get token
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": "taskuser@example.com", "password": "securepassword"}
    )
    response = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "taskuser@example.com", "password": "securepassword"}
    )
    token = response.json()["access_token"]
    async_client.headers = {"Authorization": f"Bearer {token}"}
    return async_client

async def test_create_task(auth_client: AsyncClient):
    response = await auth_client.post(
        "/api/v1/tasks/",
        json={"title": "Test Task", "description": "Description here", "priority": "high"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert "id" in data
    
async def test_get_tasks(auth_client: AsyncClient):
    # Ensure there's a task
    await auth_client.post(
        "/api/v1/tasks/",
        json={"title": "List Task", "description": "List desc", "priority": "medium"}
    )
    
    response = await auth_client.get("/api/v1/tasks/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

async def test_get_task_by_id(auth_client: AsyncClient):
    create_resp = await auth_client.post(
        "/api/v1/tasks/",
        json={"title": "Single Task", "description": "Desc"}
    )
    task_id = create_resp.json()["id"]
    
    response = await auth_client.get(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Single Task"

async def test_update_task(auth_client: AsyncClient):
    create_resp = await auth_client.post(
        "/api/v1/tasks/",
        json={"title": "Update Me", "description": "Old desc"}
    )
    task_id = create_resp.json()["id"]
    
    response = await auth_client.put(
        f"/api/v1/tasks/{task_id}",
        json={"title": "Updated", "description": "New desc"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated"
    assert data["description"] == "New desc"

async def test_delete_task(auth_client: AsyncClient):
    create_resp = await auth_client.post(
        "/api/v1/tasks/",
        json={"title": "Delete Me", "description": "To be deleted"}
    )
    task_id = create_resp.json()["id"]
    
    response = await auth_client.delete(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 200
    
    # Verify deletion (assuming it returns 404 now or soft deletion works on GET)
    get_resp = await auth_client.get(f"/api/v1/tasks/{task_id}")
    assert get_resp.status_code == 404

@pytest.mark.asyncio
async def test_upload_task_attachment(auth_client: AsyncClient):
    # Create a task
    task_data = {
        "title": "Task for Upload",
        "description": "Will upload a file here",
        "priority": "low"
    }
    create_resp = await auth_client.post("/api/v1/tasks/", json=task_data)
    assert create_resp.status_code == 201
    task_id = create_resp.json()["id"]

    # Upload file
    file_content = b"This is a test file for upload."
    files = {"file": ("test_upload.txt", file_content, "text/plain")}
    
    response = await auth_client.post(
        f"/api/v1/tasks/{task_id}/upload",
        files=files
    )
    assert response.status_code == 201
    
    data = response.json()
    assert data["filename"] == "test_upload.txt"
    assert data["content_type"] == "text/plain"
    assert data["size"] == len(file_content)
    assert data["task_id"] == task_id
    assert "id" in data

@pytest.mark.asyncio
async def test_search_tasks(auth_client: AsyncClient):
    # Create tasks
    await auth_client.post("/api/v1/tasks/", json={"title": "Find an Apple", "description": "This is a fruit", "priority": "low"})
    await auth_client.post("/api/v1/tasks/", json={"title": "Find a Banana", "description": "Another yellow thing", "priority": "low"})
    
    # Search for Apple
    response = await auth_client.get("/api/v1/tasks/?search=Apple")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any("Apple" in task["title"] for task in data)
    assert not any("Banana" in task["title"] for task in data)
    
    # Search for yellow
    response2 = await auth_client.get("/api/v1/tasks/?search=yellow")
    assert response2.status_code == 200
    data2 = response2.json()
    assert len(data2) >= 1
    assert any("Banana" in task["title"] for task in data2)
