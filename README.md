# SecureTaskAPI

![CI/CD](https://github.com/YOUR_USERNAME/SecureTaskAPI/actions/workflows/ci-cd.yml/badge.svg)

Production REST API built with FastAPI, PostgreSQL, Redis, Docker, and AWS.

## Live Demo
**Base URL:** http://13.60.187.151  
**API Docs:** http://13.60.187.151/docs  
**Health Check:** http://13.60.187.151/health

## Features
- JWT authentication with refresh token blacklisting on logout
- Role-Based Access Control (Admin / User)
- Redis-backed rate limiting (5 req/min) on auth endpoints
- Full CRUD for tasks with ownership-based access control
- Multi-stage Docker build with docker-compose
- GitHub Actions CI/CD — lint, test, deploy on every push to main

## Stack
- **Backend:** Python 3.11 / FastAPI
- **Database:** PostgreSQL 15 + SQLAlchemy + Alembic
- **Cache:** Redis 7
- **Infrastructure:** AWS EC2 + nginx
- **DevOps:** Docker / Docker Compose / GitHub Actions

## API Endpoints
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | /users/ | Public | Register user |
| POST | /auth/login | Public | Login, get token |
| POST | /auth/logout | Required | Blacklist token |
| GET | /users/me | Required | Get own profile |
| GET | /users/ | Admin only | List all users |
| POST | /tasks/ | Required | Create task |
| GET | /tasks/ | Required | Get own tasks |
| PUT | /tasks/{id} | Required | Update task |
| DELETE | /tasks/{id} | Required | Delete task |

## Local Development
```bash
git clone https://github.com/YOUR_USERNAME/SecureTaskAPI.git
cd SecureTaskAPI
cp .env.example .env  # add your values
docker compose up --build
```

## Running Tests
```bash
pytest tests/ -v --cov=app --cov-report=term-missing
```
