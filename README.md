# Vehicle Rental Management System (REST API)

A production-grade REST API backend built with **Python 3.11+**, **FastAPI**, **SQLAlchemy 2.x**, **PostgreSQL**, and **Alembic**.

---

## 1. What You Need to Install on This Machine

Since this is your personal machine, here is exactly what you need installed before running the project:

### A. Python (Already installed on your machine)
- Python **3.11+** (You have Python 3.13.3 installed).

### B. PostgreSQL Database
You need a running PostgreSQL server. You can install it using either method:
1. **Via Windows Package Manager (PowerShell as Admin):**
   ```powershell
   winget install PostgreSQL.PostgreSQL
   ```
2. **Or via the official installer:**
   - Download and run the Windows installer from [EnterpriseDB PostgreSQL](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads).
   - Set the master password for the `postgres` user (e.g. `postgres`).
   - Leave the default port as `5432`.

### C. Create the Database
Once PostgreSQL is installed and running, create the database `vehicle_rental_db`:
- Using `psql` (or pgAdmin):
  ```sql
  CREATE DATABASE vehicle_rental_db;
  ```

---

## 2. Project Setup & Installation

### Step 1: Open Terminal in the Project Directory
```powershell
cd "S:\Case study"
```

### Step 2: Create and Activate Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables (`.env`)
The project comes with pre-configured `.env` and `.env.example` files:
```env
PROJECT_NAME="Vehicle Rental Management System"
API_V1_PREFIX=""
SECRET_KEY="super-secret-jwt-token-key-change-in-production"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/vehicle_rental_db
CORS_ORIGINS=["http://localhost", "http://localhost:8000", "http://127.0.0.1:8000"]
LOGIN_RATE_LIMIT_PER_MINUTE=10
```
*(If your postgres password is different, adjust `DATABASE_URL` in `.env` accordingly).*

### Step 5: Run Database Migrations (Alembic)
Run the Alembic migrations to construct the database schema from empty:
```powershell
alembic upgrade head
```

### Step 6: Seed the Database with Master Data & Demo Users
Run the automated seed script to populate branches, vehicle categories, vehicles, tariffs, demo accounts, and a sample completed rental:
```powershell
python seed.py
```

### Step 7: Start the FastAPI Server
```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- Interactive Swagger UI Documentation: **http://127.0.0.1:8000/docs**
- ReDoc Documentation: **http://127.0.0.1:8000/redoc**
- Health Check: **http://127.0.0.1:8000/health**

---

## 3. Seeded Demo Accounts

| Role | Email | Password | Details / Permissions |
| :--- | :--- | :--- | :--- |
| **ADMIN** | `admin@rentalapp.com` | `Admin@123` | Full administrative control, branches, categories, fleet, tariffs, reports |
| **BRANCH_STAFF** | `staff.mumbai@rentalapp.com` | `Staff@123` | Linked to **Mumbai Central Branch** (Branch 1) |
| **BRANCH_STAFF** | `staff.delhi@rentalapp.com` | `Staff@123` | Linked to **Delhi Airport Hub** (Branch 2) |
| **CUSTOMER** (Verified) | `customer.verified@rentalapp.com` | `Customer@123` | Driving licence verified (`licence_verified=True`), can book immediately |
| **CUSTOMER** (Unverified) | `customer.unverified@rentalapp.com` | `Customer@123` | New customer with unverified licence |

---

## 4. Running Automated Tests & Coverage

The test suite covers all acceptance criteria with **88% code coverage**:
```powershell
pytest --cov=app --cov-report=term-missing tests/
```

### Key Acceptance Tests Proven:
1. **Conflict-Free Overlapping Booking Rejection (`test_bookings.py`)**:
   - Partial overlap at start ($[T-1, T+1]$ vs $[T, T+2]$)
   - Partial overlap at end ($[T+1, T+3]$ vs $[T, T+2]$)
   - Full containment outer ($[T-1, T+3]$ vs $[T, T+2]$)
   - Full containment inner ($[T+0.5, T+1.5]$ vs $[T, T+2]$)
   - Exact match ($[T, T+2]$ vs $[T, T+2]$)
2. **Cheapest-Rate Pricing Algorithm (`test_pricing.py`)**:
   - 5 hours rental
   - 2 days rental (48 hours)
   - 10 days rental (240 hours)
3. **Cross-Branch Authorization Enforcement (`test_rentals.py`)**:
   - Branch-staff account cannot act on or pickup another branch's booking.
4. **IDOR & Security Controls**:
   - Customers cannot view another customer's bookings or invoices.
   - Authentication failure (wrong password returns 401).
   - Authorization failure (wrong role returns 403).
   - Validation failure (invalid input returns 422).

---

## 5. API Surface Summary

| HTTP Method | Endpoint | Allowed Roles | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/register` | Public | Register as a customer with licence number |
| `POST` | `/auth/login` | Public | Authenticate and obtain JWT access token |
| `POST` | `/auth/staff` | `ADMIN` | Create branch-staff account linked to branch |
| `PATCH` | `/customers/{id}/verify-licence` | `BRANCH_STAFF` | Verify customer driving licence |
| `POST` | `/branches` | `ADMIN` | Create a new branch |
| `GET` | `/branches` | Public | List branches with city filter, sort, pagination |
| `PATCH` | `/branches/{id}` | `ADMIN` | Update branch address or contact details |
| `POST` | `/vehicle-categories` | `ADMIN` | Create vehicle category (Hatchback, SUV, etc.) |
| `GET` | `/vehicle-categories` | Public | List categories with pagination |
| `POST` | `/vehicles` | `ADMIN` | Register new vehicle into branch fleet |
| `GET` | `/vehicles` | Public | List and filter fleet by branch, category, status |
| `PATCH` | `/vehicles/{id}/status` | `BRANCH_STAFF` | Mark vehicle status (e.g. `UNDER_MAINTENANCE`) |
| `POST` | `/tariffs` | `ADMIN` | Define rates, free km, and security deposit |
| `GET` | `/tariffs` | Public | List category tariffs |
| `GET` | `/availability` | Public / Customer | Conflict-free vehicle search for date-time window |
| `POST` | `/bookings/quote` | `CUSTOMER` | Estimate rental amount before booking |
| `POST` | `/bookings` | `CUSTOMER` | Book available vehicle (checks licence & window) |
| `GET` | `/bookings/me` | `CUSTOMER` | View own bookings history |
| `GET` | `/bookings/{id}` | Customer / Staff / Admin | View single booking details (with IDOR check) |
| `PATCH` | `/bookings/{id}/cancel` | `CUSTOMER` | Cancel booking under policy (>24h 100%, <24h 50%) |
| `GET` | `/bookings/branch` | `BRANCH_STAFF` | View all bookings for staff's branch on a date |
| `POST` | `/rentals/{booking_id}/pickup` | `BRANCH_STAFF` | Record pickup (odometer & fuel), status -> `BOOKED` |
| `POST` | `/rentals/{booking_id}/return` | `BRANCH_STAFF` | Record return, generate invoice, status -> `AVAILABLE` |
| `GET` | `/invoices/{rental_id}` | Customer / Staff / Admin | View final itemized settlement invoice |
| `GET` | `/reports/utilisation` | `ADMIN` | Fleet utilisation report per branch over date range |
| `GET` | `/reports/revenue` | `ADMIN` | Revenue report grouped by branch and category |
| `GET` | `/health` | Public | Application & database connection health check |

---

## 6. Architecture & Clean Code Compliance

This project adheres strictly to the **3-Layer Monolithic Architecture** specified in the guidelines:
```
app/
├── main.py              # FastAPI app, middleware, global exception handlers
├── exceptions.py        # Custom typed exceptions (AppException, ConflictException, etc.)
├── core/
│   ├── config.py        # Pydantic BaseSettings loaded from .env
│   └── security.py      # Passlib bcrypt hashing, JWT create/verify, role dependencies
├── db/
│   ├── base.py          # SQLAlchemy 2.0 DeclarativeBase with timestamp mixin
│   └── session.py       # Engine, SessionLocal, get_db dependency
├── models/              # SQLAlchemy ORM models (users, branches, vehicles, tariffs, bookings, rentals, invoices)
├── schemas/             # Pydantic v2 validation models
├── repositories/        # Database access layer (no business logic, no HTTP objects)
├── services/            # Business logic orchestration, validation, pricing algorithm
└── routers/             # Thin FastAPI APIRouters (delegates to services)
```
- **No SQL or business logic in routers**.
- **No HTTP objects (`Request`, `Response`, `HTTPException`) in services**.
- **Structured JSON errors**: `{"detail": "...", "code": "..."}` for all error responses without leaking stack traces.
- **Licence Number Masking**: Masked as `XX****1234` in responses and never written to logs.
- **Monetary Precision**: All currency values use `Numeric(12, 2)` (Python `Decimal`) — never float.
