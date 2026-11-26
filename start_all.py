import sys
import subprocess
import time
import socket
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def service_python(service_dir: Path) -> Path:
    if sys.platform == "win32":
        candidate = service_dir / ".venv" / "Scripts" / "python.exe"
    else:
        candidate = service_dir / ".venv" / "bin" / "python"
    if candidate.exists():
        return candidate
    raise FileNotFoundError(
        f"Virtual environment not found for {service_dir.name}: {candidate}. "
        "Create it and install that service's requirements before starting."
    )


def ensure_ports_available(services: list[tuple[str, int]]) -> None:
    occupied = []
    for name, port in services:
        with socket.socket() as connection:
            connection.settimeout(0.25)
            if connection.connect_ex(("127.0.0.1", port)) == 0:
                occupied.append(f"{name} ({port})")
    if occupied:
        raise RuntimeError(
            "Cannot start services because these ports are already in use: "
            + ", ".join(occupied)
            + ". Stop the old service processes and retry."
        )


def start():
    services = [
        ("auth-service", 8001),
        ("fleet-service", 8002),
        ("catalog-service", 8005),
        ("booking-service", 8003),
        ("rental-operations-service", 8004),
        ("api-gateway", 8000),
    ]
    ensure_ports_available(services)

    # Windows flags to ensure background processes survive after script exits
    DETACHED = 0x00000008 | 0x00000200 if sys.platform == "win32" else 0

    for name, port in services:
        cwd = ROOT / name
        module = "main:app" if name == "api-gateway" else "app.main:app"
        subprocess.Popen(
            [
                str(service_python(cwd)),
                "-m",
                "uvicorn",
                module,
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
                "--reload",
            ],
            cwd=cwd,
            creationflags=DETACHED,
            close_fds=True,
        )
        print(f"[OK] Started {name} on http://127.0.0.1:{port}")
        time.sleep(1)

    print("\nWaiting for services to finish starting...")
    time.sleep(3)
    print("All microservices are up and running!")
    print("  API Gateway:   http://127.0.0.1:8000")
    print("  Catalog:       http://127.0.0.1:8005")
    print("  Swagger UI:    http://127.0.0.1:8000/docs")
    print("  Health Check:  http://127.0.0.1:8000/health")

if __name__ == "__main__":
    start()
