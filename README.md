# Task Manager API Backend

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-%23ffffff.svg?style=for-the-badge&logo=pytest&logoColor=2f9fe3)
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white)

A robust, asynchronous Task Manager API built with **FastAPI**, **SQLAlchemy 2.0 (aiosqlite)**, and **Pydantic v2**. This project provides a complete backend foundation for managing users, tasks, categories, and file attachments, equipped with strong security, role-based access control (RBAC), and advanced search capabilities.

## Features

- **Authentication & Authorization**: Secure JWT-based authentication using modern cryptography (bcrypt). Includes standard User permissions and Role-Based Access Control (RBAC) via Admin middlewares.
- **RESTful CRUD Operations**: Create, Read, Update, and Delete endpoints for Tasks and Categories.
- **Advanced Relationships**: Many-to-many database relationships seamlessly mapping `Tasks` to multiple `Categories`.
- **File Uploads**: Attach file payloads to existing tasks with asynchronous async/await streaming powered by `aiofiles`.
- **Advanced Querying & Pagination**: Filter tasks by priority, status, category, sorting order, and full-text `search` (ILIKE match on titles and descriptions).
- **Rate Limiting**: Integrated `slowapi` to protect sensitive routes (registration and login) from abuse.
- **Automated Testing Suite**: High coverage with 11 parallel-safe asynchronous API tests running through an isolated, in-memory SQLite database via `pytest` and `httpx`.
- **Database Migrations**: Integrated configurations with `Alembic` for automated DB schema upgrades and rollbacks.

## Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **ORM & Database**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (Async with `aiosqlite`)
- **Data Validation**: [Pydantic v2](https://docs.pydantic.dev/latest/)
- **Authentication**: `python-jose` (JWT) & `passlib[bcrypt]`
- **Rate Limiting**: `slowapi`
- **Testing**: `pytest`, `pytest-asyncio`, `httpx`
- **Migrations**: `alembic`

## Folder Structure

```text
task-manager-api/
├── alembic/                # Database migrations (Alembic)
├── alembic.ini             # Alembic configuration
├── app/
│   ├── api/
│   │   ├── deps.py         # FastAPI dependencies (auth, RBAC, DB session)
│   │   └── v1/             # API version 1 Router definitions
│   ├── core/
│   │   ├── config.py       # Pydantic Settings & Env vars
│   │   ├── exceptions.py   # Centralized HTTP Exception Handling
│   │   ├── rate_limit.py   # SlowAPI Limiter Configuration
│   │   └── security.py     # Hashing and JWT Utilities
│   ├── db/
│   │   ├── base.py         # SQLAlchemy Declarative Base
│   │   └── session.py      # Async Engine and SessionMaker
│   ├── models/             # SQLAlchemy Models (User, Task, Category, Attachment)
│   ├── schemas/            # Pydantic DTOs for serialization
│   └── services/           # Business Logic layer
├── tests/                  # Pytest asynchronous test suite
├── main.py                 # FastAPI Application Entrypoint
├── pyproject.toml          # Project metadata and dependencies (uv/pip)
├── README.md
└── .gitignore
```

## Installation & Setup

### 1. Requirements

- Python 3.10+
- `pip` or preferably [uv](https://github.com/astral-sh/uv)

### 2. Clone the repository

```bash
git clone <your-repository-url>
cd task-manager-api
```

### 3. Setup Virtual Environment

If you are using `uv`:
```bash
uv venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate
uv pip install -e .
```

If you are using standard `pip`:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate
pip install -e .
```

### 4. Setup Environment Variables

The project uses `pydantic-settings`. Default variables are securely populated, but you can override them via a `.env` file at the root:

```env
PROJECT_NAME="Task Manager API"
VERSION="1.0.0"
API_V1_STR="/api/v1"
SECRET_KEY="your-super-secret-key-change-in-production"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL="sqlite+aiosqlite:///./task_manager.db"
```

### 5. Run Database Migrations

Generate the local SQLite database schema by running:
```bash
alembic upgrade head
```

## Running the Application

Start the local development server utilizing top-speed concurrent ASGI (`uvicorn` recommended):

```bash
uvicorn main:app --reload
```

The API will be accessible at: `http://localhost:8000`

## Documentation & Exploring the API

FastAPI automatically generates comprehensive interactive documentation. Once the server is running, navigate to:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Running Tests

An independent, local `pytest` configuration relies on an in-memory SQLite database (`sqlite+aiosqlite:///:memory:`). No production or local file databases are affected.

```bash
pytest tests/ -v
```

## Contributing

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
