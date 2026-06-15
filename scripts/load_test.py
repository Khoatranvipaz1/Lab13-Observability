import argparse
import concurrent.futures
import json
import time
from pathlib import Path

import httpx

BASE_URL = "http://127.0.0.1:8000"
QUERIES = Path("data/sample_queries.jsonl")


def check_server() -> None:
    try:
        response = httpx.get(f"{BASE_URL}/health", timeout=3.0)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise SystemExit(
            "Server is unavailable. Start it first with:\n"
            "  .\\venv\\Scripts\\python.exe -m uvicorn "
            "app.main:app --host 127.0.0.1 --port 8000"
        ) from exc


def send_request(payload: dict) -> tuple[bool, str]:
    try:
        start = time.perf_counter()
        with httpx.Client(timeout=30.0) as client:
            r = client.post(f"{BASE_URL}/chat", json=payload)
        latency = (time.perf_counter() - start) * 1000
        message = (
            f"[{r.status_code}] {r.json().get('correlation_id')} | "
            f"{payload['feature']} | {latency:.1f}ms"
        )
        return r.is_success, message
    except Exception as e:
        return False, f"Error: {e}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--concurrency", type=int, default=1, help="Number of concurrent requests")
    args = parser.parse_args()
    if args.concurrency < 1:
        parser.error("--concurrency must be at least 1")

    lines = [line for line in QUERIES.read_text(encoding="utf-8").splitlines() if line.strip()]
    check_server()

    payloads = [json.loads(line) for line in lines]
    results: list[bool] = []
    if args.concurrency > 1:
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=args.concurrency
        ) as executor:
            futures = [executor.submit(send_request, payload) for payload in payloads]
            for future in concurrent.futures.as_completed(futures):
                success, message = future.result()
                results.append(success)
                print(message, flush=True)
    else:
        for payload in payloads:
            success, message = send_request(payload)
            results.append(success)
            print(message, flush=True)

    passed = sum(results)
    print(f"Completed: {passed}/{len(results)} successful requests")
    if passed != len(results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
