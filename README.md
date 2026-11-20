# Vehicle Rental Management System

This project is currently at its initial setup stage. Its running API contains **nine business endpoints and one health endpoint**. There is no login, authentication, token, or authorization flow.

## Current endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Check service and database status |
| `POST` | `/customers` | Create a customer profile |
| `POST` | `/branches` | Create a branch |
| `GET` | `/branches` | List/search branches |
| `POST` | `/vehicle-categories` | Create a vehicle category |
| `GET` | `/vehicle-categories` | List vehicle categories |
| `POST` | `/vehicles` | Add a vehicle |
| `GET` | `/vehicles` | List/filter vehicles |
| `POST` | `/tariffs` | Create a category tariff |
| `GET` | `/tariffs` | List tariffs |

Other modules will be added in later stages. Open `http://127.0.0.1:8000/docs` to try the current API; no authorization header is needed.

## Run locally

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Set DATABASE_URL in .env to a PostgreSQL or MySQL database.
alembic upgrade head
python seed.py
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The seed script adds sample branches, categories, vehicles, tariffs, and a customer. It skips seeding if the sample Mumbai branch already exists.

Example request bodies are in [SWAGGER_DATA_CHEAT_SHEET.md](SWAGGER_DATA_CHEAT_SHEET.md) and [requests.http](requests.http).
