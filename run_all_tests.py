import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SERVICES = {
    "auth-service": {
        "stories": {
            "F01": "Customer registration",
            "F02": "Customer login",
            "F03": "Create branch staff",
            "F04": "Verify customer licence",
        },
        "rules": {},
    },
    "fleet-service": {
        "stories": {
            "F05": "Manage branches",
            "F07": "Register vehicles",
            "F08": "Update vehicle status",
            "F09": "List and filter fleet",
        },
        "rules": {},
    },
    "catalog-service": {
        "stories": {
            "F06": "Manage vehicle categories",
            "F10": "Define category tariffs",
            "F11": "Configure rental fees",
        },
        "rules": {},
    },
    "booking-service": {
        "stories": {
            "F12": "Search vehicle availability",
            "F13": "Get a booking quote",
            "F14": "Create a booking",
            "F15": "View bookings",
            "F16": "Cancel a booking",
            "F17": "View branch bookings",
        },
        "rules": {
            "B01": "Cheapest hourly/daily/weekly pricing",
            "B02": "Non-overlapping booking periods",
            "B03": "Verified licence required to book",
            "B07": "Future pickup and four-hour minimum",
            "B08": "Time-based cancellation refunds",
            "B09": "Unavailable vehicles cannot be booked",
            "B10": "Branch staff access is branch-restricted",
        },
    },
    "rental-operations-service": {
        "stories": {
            "F18": "Record vehicle pickup",
            "F19": "Record return and create invoice",
            "F20": "Calculate final rental charges",
            "F21": "Retrieve settlement invoice",
            "F22": "View fleet utilisation report",
            "F23": "View revenue report",
        },
        "rules": {
            "B04": "Odometer cannot decrease",
            "B05": "Pickup requires confirmed booking",
            "B06": "Return requires in-progress rental",
        },
    },
    "api-gateway": {
        "stories": {"G01": "Route catalog API requests"},
        "rules": {},
    },
}


def service_python(service_dir: Path) -> Path:
    if sys.platform == "win32":
        python = service_dir / ".venv" / "Scripts" / "python.exe"
    else:
        python = service_dir / ".venv" / "bin" / "python"
    return python if python.exists() else Path(sys.executable)


def run_service_tests(service: str, report_dir: Path) -> dict:
    service_dir = ROOT / service
    test_dir = service_dir / "tests"
    report_file = report_dir / f"{service}.xml"
    if not test_dir.is_dir():
        return {
            "passed": False,
            "output": "No tests/ folder\n",
            "testcases": [],
        }

    command = [
        str(service_python(service_dir)),
        "-m",
        "pytest",
        str(test_dir),
        "-q",
        f"--junitxml={report_file}",
    ]
    result = subprocess.run(
        command,
        cwd=service_dir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    testcases = []
    if report_file.exists():
        root = ET.parse(report_file).getroot()
        for testcase in root.iter("testcase"):
            failed = any(
                child.tag in {"failure", "error", "skipped"}
                for child in testcase
            )
            testcases.append(
                {"name": testcase.attrib.get("name", ""), "passed": not failed}
            )

    return {
        "passed": result.returncode == 0,
        "output": result.stdout,
        "testcases": testcases,
    }


def requirement_passed(testcases: list[dict], requirement_id: str) -> bool:
    matches = [
        testcase
        for testcase in testcases
        if testcase["name"].startswith(f"test_req_{requirement_id}")
        or testcase["name"].startswith(f"test_rule_{requirement_id}")
    ]
    return bool(matches) and all(testcase["passed"] for testcase in matches)


def print_score(label: str, passed: int, total: int) -> None:
    percentage = (passed / total * 100) if total else 0
    print(f"{label}: {passed}/{total} ({percentage:.1f}%)")


def main() -> int:
    results = {}
    with tempfile.TemporaryDirectory(prefix="rental-tests-") as temp_dir:
        report_dir = Path(temp_dir)
        for service, inventory in SERVICES.items():
            result = run_service_tests(service, report_dir)
            results[service] = result
            print(f"\n{'=' * 18} {service} {'=' * 18}")
            print(result["output"], end="" if result["output"].endswith("\n") else "\n")

    print("\n========== FUNCTIONAL REQUIREMENT SUMMARY ==========")
    print(f"{'Service':30} {'Stories/criteria':20} {'Coverage':12} {'Suite'}")
    print("-" * 78)

    total_criteria = 0
    passed_criteria = 0
    total_user_stories = 0
    passed_user_stories = 0
    total_gateway_criteria = 0
    passed_gateway_criteria = 0
    total_rules = 0
    passed_rules = 0
    suite_results = []
    for service, inventory in SERVICES.items():
        result = results[service]
        story_ids = inventory["stories"]
        rule_ids = inventory["rules"]
        service_story_count = sum(
            requirement_passed(result["testcases"], requirement_id)
            for requirement_id in story_ids
        )
        service_rule_count = sum(
            requirement_passed(result["testcases"], requirement_id)
            for requirement_id in rule_ids
        )
        total_criteria += len(story_ids)
        passed_criteria += service_story_count
        user_story_ids = [item for item in story_ids if item.startswith("F")]
        gateway_ids = [item for item in story_ids if item.startswith("G")]
        total_user_stories += len(user_story_ids)
        passed_user_stories += sum(
            requirement_passed(result["testcases"], requirement_id)
            for requirement_id in user_story_ids
        )
        total_gateway_criteria += len(gateway_ids)
        passed_gateway_criteria += sum(
            requirement_passed(result["testcases"], requirement_id)
            for requirement_id in gateway_ids
        )
        total_rules += len(rule_ids)
        passed_rules += service_rule_count
        suite = "PASS" if result["passed"] else "FAIL"
        suite_results.append(result["passed"])
        print(
            f"{service:30} "
            f"{service_story_count}/{len(story_ids):<18} "
            f"{service_story_count / len(story_ids) * 100 if story_ids else 0:>5.1f}%      "
            f"{suite}"
        )
        if rule_ids:
            print(
                f"  Business rules: {service_rule_count}/{len(rule_ids)} "
                f"({service_rule_count / len(rule_ids) * 100:.1f}%)"
            )

    print("-" * 78)
    print_score("Overall vehicle-rental user stories", passed_user_stories, total_user_stories)
    print_score("Gateway integration criteria", passed_gateway_criteria, total_gateway_criteria)
    print_score("Overall functional criteria", passed_criteria, total_criteria)
    print_score("Overall business rules", passed_rules, total_rules)
    print(
        "Note: each story or rule counts as covered only when its mapped test "
        "exists and all matching test cases pass. These percentages measure "
        "tested requirement checks, not line coverage or full certification."
    )
    all_criteria_passed = (
        passed_criteria == total_criteria and passed_rules == total_rules
    )
    return 0 if all(suite_results) and all_criteria_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
