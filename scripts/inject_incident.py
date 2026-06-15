from __future__ import annotations

import argparse
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

BASE_URL = "http://127.0.0.1:8000"
load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", required=True, choices=["rag_slow", "tool_fail", "cost_spike"])
    parser.add_argument("--disable", action="store_true")
    args = parser.parse_args()

    path = f"/incidents/{args.scenario}/disable" if args.disable else f"/incidents/{args.scenario}/enable"
    token = os.getenv("INCIDENT_ADMIN_TOKEN")
    if not token:
        raise SystemExit("INCIDENT_ADMIN_TOKEN is not configured in .env")
    r = httpx.post(
        f"{BASE_URL}{path}",
        headers={"x-admin-token": token},
        timeout=10.0,
    )
    print(r.status_code, r.json())


if __name__ == "__main__":
    main()
