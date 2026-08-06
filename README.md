# TaskHub API 🚀

> Hệ thống quản lý công việc (Task Management System) xây dựng bằng **FastAPI** + **SQLAlchemy Async** + **MySQL**.
> Dự án thực tập tại **Sun Asterisk** — Module FastAPI Backend.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI (Python 3.11+) |
| Database | MySQL 8.0 |
| ORM | SQLAlchemy 2.x (Async mode) |
| Migration | Alembic |
| Cache | Redis 7 |
| Authentication | JWT — python-jose + passlib (bcrypt) |
| Validation | Pydantic v2 |
| Linter | Ruff + mypy |
| Containerization | Docker + Docker Compose |

---

## Kiến trúc dự án

Dự án áp dụng **Layered Architecture**:

```
Request → Router → Repository → Database
```

```
taskhub-api/
├── app/
│   ├── core/
│   │   ├── config.py          # Cấu hình app (load từ .env)
│   │   ├── database.py        # SQLAlchemy engine & session
│   │   ├── security.py        # Hash password, tạo JWT token
│   │   └── dependencies.py   # FastAPI dependencies (get_current_user, RBAC)
│   ├── models/
│   │   ├── base.py            # DeclarativeBase
│   │   └── domain.py          # 8 SQLAlchemy ORM models
│   ├── schemas/
│   │   ├── auth.py            # Token schemas
│   │   ├── user.py            # User schemas
│   │   ├── workspace.py       # Workspace & Member schemas
│   │   ├── project.py         # Project schemas
│   │   ├── task.py            # Task schemas + Enums
│   │   ├── comment.py         # Comment schemas
│   │   ├── label.py           # Label schemas
│   │   └── query.py           # Filter & Pagination schemas
│   ├── repositories/
│   │   ├── base.py            # Generic BaseRepository[Model, Create, Update]
│   │   ├── user.py
│   │   ├── workspace.py
│   │   ├── project.py
│   │   ├── task.py
│   │   ├── comment.py
│   │   └── label.py
│   ├── routers/
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── workspaces.py
│   │   ├── projects.py        # Project CRUD + Task CRUD (nested)
│   │   ├── comments.py
│   │   └── labels.py
│   └── main.py
├── alembic/                   # Database migrations
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml             # Ruff + mypy config
├── requirements.txt
└── .env.example
```

---

## Database Schema

```
users
  └──< workspaces (owner_id)
         └──< workspace_members (workspace_id, user_id) — N:N
         └──< projects
                └──< tasks (project_id, assignee_id, created_by)
                │     └──< comments (task_id, author_id)
                │     └──>< labels (task_labels) — N:N
                └──< labels (project_id)
```

---

## Cài đặt và Chạy

### Yêu cầu
- [Docker](https://docs.docker.com/get-docker/) & Docker Compose

### 1. Clone repository
```bash
git clone https://github.com/trieuminhpham/taskhub-api.git
cd taskhub-api
```

### 2. Cấu hình biến môi trường
```bash
cp .env.example .env
```

Nội dung file `.env`:
```env
APP_NAME=TaskHub
DEBUG=false

DB_HOST=db
DB_PORT=3306
DB_USER=root
DB_PASSWORD=root
DB_NAME=taskhub

REDIS_HOST=redis
REDIS_PORT=6379

SECRET_KEY=super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 3. Khởi động toàn bộ services
```bash
docker compose up -d --build
```

### 4. Chạy database migration (chỉ lần đầu)
```bash
docker compose exec api alembic upgrade head
```

### 5. Truy cập API
| URL | Mô tả |
|-----|-------|
| http://localhost:8000/docs | Swagger UI (interactive) |
| http://localhost:8000/redoc | ReDoc (đẹp hơn, dành cho review) |
| http://localhost:8000/health | Health check |

---

## API Endpoints

### 🔐 Authentication
| Method | URL | Mô tả |
|--------|-----|-------|
| `POST` | `/api/v1/auth/register` | Đăng ký tài khoản mới |
| `POST` | `/api/v1/auth/login` | Đăng nhập, nhận Access & Refresh Token |
| `POST` | `/api/v1/auth/refresh` | Làm mới Access Token bằng Refresh Token |

### 👤 User Profile
| Method | URL | Mô tả |
|--------|-----|-------|
| `GET` | `/api/v1/users/me` | Xem thông tin cá nhân |
| `PATCH` | `/api/v1/users/me` | Cập nhật thông tin cá nhân |
| `POST` | `/api/v1/users/me/password` | Đổi mật khẩu |

### 🏢 Workspace
| Method | URL | Mô tả | Quyền |
|--------|-----|-------|-------|
| `GET` | `/api/v1/workspaces/` | Danh sách workspace của tôi | Member |
| `POST` | `/api/v1/workspaces/` | Tạo workspace mới | Đăng nhập |
| `GET` | `/api/v1/workspaces/{id}` | Chi tiết workspace | Member |
| `PATCH` | `/api/v1/workspaces/{id}` | Sửa tên workspace | EDITOR+ |
| `DELETE` | `/api/v1/workspaces/{id}` | Xóa workspace | OWNER |

### 👥 Workspace Members
| Method | URL | Mô tả | Quyền |
|--------|-----|-------|-------|
| `GET` | `/api/v1/workspaces/{id}/members` | Danh sách thành viên | Member |
| `POST` | `/api/v1/workspaces/{id}/members` | Mời thành viên | OWNER |
| `PATCH` | `/api/v1/workspaces/{id}/members/{uid}` | Đổi quyền thành viên | OWNER |
| `DELETE` | `/api/v1/workspaces/{id}/members/{uid}` | Đuổi thành viên | OWNER |

### 📁 Project
| Method | URL | Mô tả | Quyền |
|--------|-----|-------|-------|
| `GET` | `/api/v1/workspaces/{wid}/projects/` | Danh sách project (filter, search, pagination) | Member |
| `POST` | `/api/v1/workspaces/{wid}/projects/` | Tạo project | EDITOR+ |
| `GET` | `/api/v1/workspaces/{wid}/projects/{pid}` | Chi tiết project | Member |
| `PATCH` | `/api/v1/workspaces/{wid}/projects/{pid}` | Sửa project | EDITOR+ |
| `DELETE` | `/api/v1/workspaces/{wid}/projects/{pid}` | Xóa project | OWNER |

**Query params cho GET `/projects/`:**
- `status` — `ACTIVE` hoặc `ARCHIVED`
- `search` — tìm theo tên
- `skip`, `limit` — phân trang

### ✅ Task
| Method | URL | Mô tả | Quyền |
|--------|-----|-------|-------|
| `GET` | `.../projects/{pid}/tasks` | Danh sách task (filter, search, pagination) | Member |
| `POST` | `.../projects/{pid}/tasks` | Tạo task | EDITOR+ |
| `GET` | `.../projects/{pid}/tasks/{tid}` | Chi tiết task | Member |
| `PATCH` | `.../projects/{pid}/tasks/{tid}` | Cập nhật task | EDITOR+ |
| `DELETE` | `.../projects/{pid}/tasks/{tid}` | Xóa task | EDITOR+ |

**Query params cho GET `/tasks`:**
- `status` — `TODO` / `IN_PROGRESS` / `IN_REVIEW` / `DONE`
- `priority` — `LOW` / `MEDIUM` / `HIGH` / `URGENT`
- `assignee_id` — ID của người được giao
- `search` — tìm theo title hoặc description
- `skip`, `limit` — phân trang

### 💬 Comment
| Method | URL | Mô tả | Quyền |
|--------|-----|-------|-------|
| `GET` | `.../tasks/{tid}/comments` | Danh sách bình luận | Member |
| `POST` | `.../tasks/{tid}/comments` | Tạo bình luận | Member |
| `PATCH` | `.../tasks/{tid}/comments/{cid}` | Sửa bình luận | Tác giả |
| `DELETE` | `.../tasks/{tid}/comments/{cid}` | Xóa bình luận | Tác giả |

### 🏷️ Label
| Method | URL | Mô tả | Quyền |
|--------|-----|-------|-------|
| `GET` | `.../projects/{pid}/labels` | Danh sách label | Member |
| `POST` | `.../projects/{pid}/labels` | Tạo label | EDITOR+ |
| `PATCH` | `.../projects/{pid}/labels/{lid}` | Sửa label | EDITOR+ |
| `DELETE` | `.../projects/{pid}/labels/{lid}` | Xóa label | OWNER |
| `POST` | `.../labels/tasks/{tid}/labels/{lid}` | Gắn label vào task | EDITOR+ |
| `DELETE` | `.../labels/tasks/{tid}/labels/{lid}` | Gỡ label khỏi task | EDITOR+ |

---

## Phân quyền RBAC

| Hành động | VIEWER | EDITOR | OWNER |
|-----------|:------:|:------:|:-----:|
| Xem Workspace / Project / Task | ✅ | ✅ | ✅ |
| Tạo / Sửa Project, Task, Label | ❌ | ✅ | ✅ |
| Xóa Project, Task | ❌ | ✅ | ✅ |
| Xóa Label | ❌ | ❌ | ✅ |
| Xóa Workspace | ❌ | ❌ | ✅ |
| Mời / Đuổi / Đổi quyền Member | ❌ | ❌ | ✅ |
| Bình luận vào Task | ✅ | ✅ | ✅ |
| Sửa / Xóa bình luận của mình | ✅ | ✅ | ✅ |

---

## Lệnh thường dùng

```bash
# Bật tất cả services
docker compose up -d

# Tắt services
docker compose down

# Xem log API
docker compose logs api -f

# Chạy migration mới
docker compose exec api alembic revision --autogenerate -m "mô tả"
docker compose exec api alembic upgrade head

# Kiểm tra code style
ruff check .
ruff check . --fix
```

---

## License

MIT © [Trieu Minh Pham](https://github.com/trieuminhpham)
