import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.pii import detect_pii

LOG_PATH = Path("data/logs.jsonl")
SCHEMA_PATH = Path("config/logging_schema.json")
ENRICHMENT_FIELDS = {"user_id_hash", "session_id", "feature", "model"}


def main() -> None:
    if not LOG_PATH.exists():
        print(f"Error: {LOG_PATH} not found. Run the app and send some requests first.")
        sys.exit(1)

    records = []
    malformed_records = 0
    pii_hits = []
    nonempty_lines = 0
    for line_number, line in enumerate(
        LOG_PATH.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not line.strip():
            continue
        nonempty_lines += 1
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            malformed_records += 1
            pii_types = detect_pii(line)
            if pii_types:
                pii_hits.append(
                    {
                        "event": "malformed_json",
                        "line": line_number,
                        "types": pii_types,
                    }
                )
            continue

    if not nonempty_lines:
        print("Error: No log records found in data/logs.jsonl")
        sys.exit(1)

    schema_errors = 0
    missing_enrichment = 0
    correlation_ids = set()
    validator = Draft202012Validator(
        json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    )

    for rec in records:
        errors = list(validator.iter_errors(rec))
        if errors:
            schema_errors += 1
            
        # Context-specific checks for API requests
        if rec.get("service") == "api":
            if "correlation_id" not in rec or rec.get("correlation_id") == "MISSING":
                schema_errors += 1
            
            if not ENRICHMENT_FIELDS.issubset(rec.keys()):
                missing_enrichment += 1

        raw = json.dumps(rec, ensure_ascii=False)
        pii_types = detect_pii(raw)
        if pii_types:
            pii_hits.append(
                {"event": rec.get("event", "unknown"), "types": pii_types}
            )

        # Collect correlation IDs
        cid = rec.get("correlation_id")
        if cid and cid != "MISSING":
            correlation_ids.add(cid)

    print("--- Lab Verification Results ---")
    print(f"Total log records analyzed: {nonempty_lines}")
    print(f"Malformed JSON records: {malformed_records}")
    print(f"Records failing JSON Schema: {schema_errors}")
    print(f"Records with missing enrichment (context): {missing_enrichment}")
    print(f"Unique correlation IDs found: {len(correlation_ids)}")
    print(f"Potential PII leaks detected: {len(pii_hits)}")
    if pii_hits:
        print(f"  Leak details: {pii_hits}")
    
    print("\n--- Grading Scorecard (Estimates) ---")
    score = 100
    if malformed_records > 0 or schema_errors > 0:
        score -= 30
        print("- [FAILED] JSONL and schema validation")
    else:
        print("+ [PASSED] JSONL and JSON schema")

    if len(correlation_ids) < 2:
        score -= 20
        print("- [FAILED] Correlation ID propagation (less than 2 unique IDs)")
    else:
        print("+ [PASSED] Correlation ID propagation")

    if missing_enrichment > 0:
        score -= 20
        print("- [FAILED] Log enrichment (missing user_id_hash, etc.)")
    else:
        print("+ [PASSED] Log enrichment")

    if pii_hits:
        score -= 30
        print("- [FAILED] PII scrubbing (found @ or test credit card)")
    else:
        print("+ [PASSED] PII scrubbing")

    print(f"\nEstimated Score: {max(0, score)}/100")

if __name__ == "__main__":
    main()
