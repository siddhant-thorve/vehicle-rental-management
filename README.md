# Vehicle Rental Management System — Microservices Architecture

A beginner-friendly vehicle rental system built with **FastAPI**, **SQLAlchemy**, and **PostgreSQL**, with a database per business service and a unified API gateway.

---

## 1. Microservices Architecture Overview

The system is decomposed into **5 autonomous business microservices** coordinated by an **API Gateway**:

The API Gateway (`http://127.0.0.1:8000`) routes requests to these services:

| Service | Port | Responsibilities | Database |
| :--- | :---: | :--- | :--- |
| Auth | 8001 | Registration, login, staff, licence verification | `rental_auth_db` |
| Fleet | 8002 | Branch locations, vehicle records, and vehicle status | `rental_fleet_db` |
| Booking | 8003 | Availability, quotes, booking creation and cancellation | `rental_service_db` |
| Rental Operations | 8004 | Pickup, returns, invoices, and reports | `rental_operations_db` |
| Catalog & Pricing | 8005 | Vehicle categories and rental tariffs | `rental_catalog_db` |

### Why this design is easy to understand:
1. **No Over-Engineering:** Every service has simple, readable files:
   - `app/main.py`: FastAPI app setup and router registration.
   - `app/core/`: Environment configuration and JWT security.
   - `app/db/`: SQLAlchemy base, engine, and session dependency.
   - `app/models/`: SQLAlchemy ORM entities.
   - `app/schemas/`: Request and response models.
   - `app/repositories/`: Database queries and transaction commits.
   - `app/services/`: Business logic and inter-service orchestration.
   - `app/routers/`: HTTP endpoints.
   - `app/exceptions.py`: Service-specific exceptions.
   - `app/seed.py`: Auth and fleet seed entry points.
   - Service roots: `auth-service/`, `fleet-service/`, `catalog-service/`, `booking-service/`, and `rental-operations-service/`. Each contains its app package, its own `.env`, requirements, and virtual environment.
2. **Database Per Service:** Business data is isolated across 5 PostgreSQL databases:
   - `rental_auth_db`
   - `rental_fleet_db`
   - `rental_catalog_db`
   - `rental_service_db` (Booking Service)
   - `rental_operations_db`
3. **API Gateway on Port 8000:**
   - Evaluator/client interacts with a single unified port `8000`.
   - Aggregated Swagger UI documentation at `http://127.0.0.1:8000/docs`.
   - Gateway routes are declared explicitly in `api-gateway/gateway/auth_routes.py`, `fleet_routes.py`, `catalog_routes.py`, `booking_routes.py`, and `operations_routes.py`. Each route forwards the request to its service using the shared helper in `gateway/proxy_utils.py`; the gateway does not use a catch-all route.
   - Internal service-to-service endpoints are called directly between services and are not exposed through the gateway.

---

## 2. Seeded Accounts & Roles

| Role | Email | Password | Description |
| :--- | :--- | :--- | :--- |
| **ADMIN** | `admin@rentalapp.com` | `Admin@123` | Full access to fleet, tariffs, staff, and reports |
| **BRANCH_STAFF** | `staff.mumbai@rentalapp.com` | `Staff@123` | Staff at Mumbai Central (Branch 1) |
| **BRANCH_STAFF** | `staff.delhi@rentalapp.com` | `Staff@123` | Staff at Delhi Airport Hub (Branch 2) |
| **CUSTOMER** (Verified) | `customer.verified@rentalapp.com` | `Customer@123` | Driving licence verified, can book vehicles |
| **CUSTOMER** (Unverified) | `customer.unverified@rentalapp.com` | `Customer@123` | New customer with unverified licence |

---

## 3. How to Run the Project (On Any Machine)

### Step 1: Create a Virtual Environment for Each Service
Open PowerShell inside `rental-microservices` and run:
```powershell
foreach ($service in @('auth-service', 'fleet-service', 'catalog-service', 'booking-service', 'rental-operations-service', 'api-gateway')) {
    python -m venv ".\$service\.venv"
    & ".\$service\.venv\Scripts\python.exe" -m pip install -r ".\$service\requirements.txt"
}
```

### Step 2: Ensure PostgreSQL Databases are Created
Create the five databases in PostgreSQL (using `psql` or pgAdmin):
```sql
CREATE DATABASE rental_auth_db;
CREATE DATABASE rental_fleet_db;
CREATE DATABASE rental_catalog_db;
CREATE DATABASE rental_service_db;
CREATE DATABASE rental_operations_db;
```
Set each service's `DATABASE_URL` in its `.env` file to match the local PostgreSQL credentials and database. Do not commit real credentials.

### Step 3: Seed All Databases
```powershell
Set-Location .\auth-service
.\.venv\Scripts\python.exe .\seed.py

Set-Location ..\catalog-service
.\.venv\Scripts\python.exe .\seed.py

Set-Location ..\fleet-service
.\.venv\Scripts\python.exe .\seed.py

Set-Location ..\rental-operations-service
.\.venv\Scripts\python.exe .\seed.py

Set-Location ..
```
The Rental Operations seed copies the existing `rentals` and `invoices` rows from `rental_service_db` into `rental_operations_db`. It preserves source data and can be rerun safely; it does not generate sample rental or invoice records.

### Step 4: Start All Microservices
```powershell
.\start_all.ps1
```
This automatically starts:
- `auth-service` on `http://127.0.0.1:8001`
- `fleet-service` on `http://127.0.0.1:8002`
- `booking-service` on `http://127.0.0.1:8003`
- `rental-operations-service` on `http://127.0.0.1:8004`
- `catalog-service` on `http://127.0.0.1:8005`
- `api-gateway` on `http://127.0.0.1:8000`

### Step 5: Open Swagger UI Documentation
Open your browser to:
- **Interactive Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### Step 6: Run the Functional Requirement Tests
```powershell
python .\run_all_tests.py
```
This runs the `tests/` folder for each service one at a time. A requirement counts as covered only when its mapped test exists and passes. The summary reports the 23 detailed user stories and gateway routing criterion, plus the 10 tracked business rules, separately. These percentages are requirement-test pass rates, not line coverage or proof that every possible behavior has been tested. The common security/API guidelines are not included in these scores.

### Step 7: Stop All Services When Done
```powershell
.\stop_all.ps1
```

---

## 4. Viva / Evaluation Questions & Answers

**Q1: Why are booking and rental operations separate services?**
> *Answer:* They own different responsibilities: Booking manages availability, quotes, and booking changes; Rental Operations manages pickup, return, invoicing, and reporting.

**Q2: How do the microservices communicate?**
> *Answer:* Synchronous REST communication using `httpx`. Booking calls Fleet for vehicle data and Catalog & Pricing for tariff data; Rental Operations calls Booking, Fleet, and Catalog & Pricing as needed.

**Q3: How is authentication handled across microservices?**
> *Answer:* Stateless JWT token propagation. The Auth Service issues the token with `sub` (user ID), `role`, and `branch_id`. Downstream services independently verify it using the shared `SECRET_KEY`.

**Q4: How did you implement Database-per-Service?**
> *Answer:* Each service connects exclusively to its own database. Rental Operations obtains booking information through Booking Service APIs instead of directly reading its database.
