import sys
import subprocess

def stop():
    ports = [8000, 8001, 8002, 8003, 8004, 8005]
    for port in ports:
        if sys.platform == "win32":
            cmd = f'powershell -Command "Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique"'
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            for pid in res.stdout.strip().splitlines():
                pid = pid.strip()
                if pid and pid.isdigit():
                    subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True)
                    print(f"[OK] Stopped process on port {port} (PID: {pid})")
    print("All microservices stopped.")

if __name__ == "__main__":
    stop()
