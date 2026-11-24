import pytest, json, warnings
from pathlib import Path
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from coverage import Coverage

warnings.filterwarnings("ignore")

_cov = Coverage.current()
_owned_cov = False
if _cov is None:
    _coverage = Coverage(source=["app"], branch=True, omit=["*/tests/*", "*/alembic/*", "*/.venv/*"])
    _coverage.erase()
    _coverage.start()
    _owned_cov = True
else:
    _coverage = _cov

from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.models import User, Branch, VehicleCategory, Vehicle, Tariff
from app.core.security import get_password_hash, create_access_token

test_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
_test_counts = {"collected": 0, "passed": 0, "failed": 0, "skipped": 0, "errors": 0}
_report_dir = Path(__file__).resolve().parent / "report"

def pytest_configure(config):
    config.addinivalue_line("filterwarnings", "ignore")
    _report_dir.mkdir(parents=True, exist_ok=True)
    xml = str(_report_dir / "test-results.xml")
    for opt in ("xmlpath", "junitxml"):
        if hasattr(config.option, opt): setattr(config.option, opt, xml)

def pytest_collection_finish(session):
    _test_counts["collected"] = len(session.items)

def pytest_runtest_logreport(report):
    if report.when != "call":
        if report.when == "setup" and report.failed: _test_counts["errors"] += 1
        return
    for k in ("passed", "failed", "skipped"):
        if getattr(report, k, False): _test_counts[k] += 1

def pytest_sessionfinish(session, exitstatus):
    global _coverage
    if _coverage is None: return
    if _owned_cov:
        _coverage.stop()
        _coverage.save()
    _report_dir.mkdir(parents=True, exist_ok=True)
    cov_json = _report_dir / "coverage.json"
    _coverage.json_report(outfile=str(cov_json), show_contexts=False)
    _coverage.html_report(directory=str(_report_dir / "coverage-html"))
    cov_pct = float(json.loads(cov_json.read_text(encoding="utf-8"))["totals"]["percent_statements_covered"])
    p, f, s, e, c = _test_counts["passed"], _test_counts["failed"], _test_counts["skipped"], _test_counts["errors"], _test_counts["collected"]
    attempted = p + f + e
    pass_pct = (p / attempted * 100.0) if attempted else 0.0
    score, st = round(pass_pct * 0.8 + cov_pct * 0.2, 2), "PASS" if f == 0 and e == 0 and cov_pct >= 80.0 else "FAIL"
    rep = {
        "generated_at": datetime.now(timezone.utc).isoformat(), "project": "vehicle-rental-management",
        "test_result": {"collected": c, "passed": p, "failed": f, "skipped": s, "errors": e, "pass_percent": round(pass_pct, 2), "status": "PASS" if f == 0 and e == 0 else "FAIL"},
        "coverage": {"line_percent": round(cov_pct, 2), "required_percent": 80.0, "status": "PASS" if cov_pct >= 80.0 else "FAIL"},
        "overall_score": {"percent": score, "formula": "80% test pass + 20% line coverage"},
        "artifacts": {"text": "test-summary.txt", "json": "test-summary.json", "coverage_json": "coverage.json", "coverage_html": "coverage-html/index.html", "junit_xml": "test-results.xml"},
        "overall_status": st
    }
    (_report_dir / "test-summary.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
    (_report_dir / "test-summary.txt").write_text(f"Vehicle Rental Management - Test Report\n{'='*48}\nGenerated: {rep['generated_at']}\n\nTEST RESULT\nCollected: {c}\nPassed: {p}\nFailed: {f}\nSkipped: {s}\nErrors: {e}\nPass percentage: {pass_pct:.2f}%\nTest status: {rep['test_result']['status']}\n\nCOVERAGE\nLine coverage: {cov_pct:.2f}%\nRequired coverage: 80.00%\nCoverage status: {rep['coverage']['status']}\n\nOVERALL SCORE\nScore: {score:.2f}%\nFormula: 80% test pass + 20% line coverage\n\nOVERALL STATUS\n{st}\n", encoding="utf-8")
    if rep["coverage"]["status"] != "PASS": session.exitstatus = pytest.ExitCode.TESTS_FAILED

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try: yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def client(db_session):
    from fastapi.testclient import TestClient
    def _get_db(): yield db_session
    app.dependency_overrides[get_db] = _get_db
    with TestClient(app) as c: yield c
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def seed_test_data(db_session):
    b1, b2 = Branch(name="Mumbai Branch", city="Mumbai", address="Mumbai Central", contact_no="9876543210"), Branch(name="Delhi Branch", city="Delhi", address="Connaught Place", contact_no="9876543211")
    db_session.add_all([b1, b2]); db_session.commit()
    users = {}
    for k, email, pwd, role, bid, lic, ver in [
        ("admin", "admin@test.com", "AdminPass123", "ADMIN", None, None, True),
        ("staff1", "staff1@test.com", "StaffPass123", "BRANCH_STAFF", b1.id, None, True),
        ("staff2", "staff2@test.com", "StaffPass123", "BRANCH_STAFF", b2.id, None, True),
        ("cust_verified", "verified@test.com", "CustPass123", "CUSTOMER", None, "MH012020009999", True),
        ("cust_unverified", "unverified@test.com", "CustPass123", "CUSTOMER", None, "DL042021008888", False),
    ]:
        u = User(email=email, password_hash=get_password_hash(pwd), full_name=k, phone="9800000000", licence_no=lic, licence_verified=ver, role=role, branch_id=bid, is_active=True)
        db_session.add(u); users[k] = u
    cat = VehicleCategory(name="Hatchback", description="Economy Car", seating_capacity=4)
    db_session.add(cat); db_session.commit()
    t = Tariff(category_id=cat.id, hourly_rate=Decimal("100"), daily_rate=Decimal("1500"), weekly_rate=Decimal("7000"), free_km_per_day=Decimal("150"), extra_km_rate=Decimal("10"), extra_hour_rate=Decimal("120"), deposit_amount=Decimal("3000"), effective_from=datetime.now(timezone.utc) - timedelta(days=1), is_active=True)
    v1 = Vehicle(registration_no="MH-01-TEST-001", category_id=cat.id, branch_id=b1.id, make="Hyundai", model="i10", fuel_type="Petrol", transmission="Manual", odometer_km=Decimal("10000"), status="AVAILABLE", is_active=True)
    v2 = Vehicle(registration_no="DL-01-TEST-002", category_id=cat.id, branch_id=b2.id, make="Maruti", model="Swift", fuel_type="Petrol", transmission="Manual", odometer_km=Decimal("20000"), status="AVAILABLE", is_active=True)
    db_session.add_all([t, v1, v2]); db_session.commit()
    return {"b1": b1, "b2": b2, "category": cat, "tariff": t, "veh1": v1, "veh2": v2, **users}

def _token(u): return {"Authorization": f"Bearer {create_access_token({'sub': str(u.id), 'role': u.role, 'branch_id': u.branch_id})}"}
@pytest.fixture
def admin_headers(seed_test_data): return _token(seed_test_data["admin"])
@pytest.fixture
def staff1_headers(seed_test_data): return _token(seed_test_data["staff1"])
@pytest.fixture
def staff2_headers(seed_test_data): return _token(seed_test_data["staff2"])
@pytest.fixture
def customer_headers(seed_test_data): return _token(seed_test_data["cust_verified"])
@pytest.fixture
def unverified_headers(seed_test_data): return _token(seed_test_data["cust_unverified"])
