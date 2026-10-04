#!/usr/bin/env python3
"""
Deterministic batch controller for inbox processing.

The AI agent analyzes one job at a time. This controller owns:
- batch membership and ordering
- current job state
- rule-set locking
- exact file movement
- append-only execution log

Usage:
  python scripts/batch_controller.py prepare
  python scripts/batch_controller.py current
  python scripts/batch_controller.py list
  python scripts/batch_controller.py complete "file.txt" ".batch/records/file.record.md"
  python scripts/batch_controller.py abort
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INBOX = ROOT / "inbox"
PROCESSED = INBOX / "processed"
OUTPUT = ROOT / "output"
BATCH = ROOT / ".batch"
MANIFEST = BATCH / "manifest.json"
LOCK = BATCH / "batch.lock"
RECORDS = BATCH / "records"
MAX_FILES = 5
AGGREGATE_INPUT = "vacancies.txt"
JOB_DELIMITER = "---JOB---"
VENV_DIR = ROOT / ".venv"
REQUIREMENTS = ROOT / "requirements.txt"

RULE_FILES = [
    "AGENTS.md",
    ".agent/rules/domain-fit-gate.md",
    ".agent/rules/anti-hallucination.md",
    ".agent/rules/workflow.md",
    ".agent/rules/keyword-emphasis.md",
    ".agent/rules/output-format.md",
    ".agent/rules/pdf-page-limit.md",
    ".agent/rules/correspondence.md",
    ".agent/rules/execution-log.md",
    ".agent/rules/agent-boundaries.md",
]


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def atomic_write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def load_manifest() -> dict:
    if not MANIFEST.exists():
        fail("No active batch. Run: python scripts/batch_controller.py prepare")
    try:
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"Invalid manifest: {exc}")


def rules_snapshot() -> dict:
    result = {}
    for rel in RULE_FILES:
        p = ROOT / rel
        if not p.is_file():
            fail(f"Required rule file is missing: {rel}")
        result[rel] = sha256(p)
    return result


def verify_rules(manifest: dict) -> None:
    current = rules_snapshot()
    locked = manifest.get("rule_hashes", {})
    if current != locked:
        changed = [p for p in RULE_FILES if current.get(p) != locked.get(p)]
        fail("Rule files changed during the batch: " + ", ".join(changed))


def ensure_no_active_batch() -> None:
    if MANIFEST.exists() or LOCK.exists():
        fail("An active batch already exists. Finish or abort it before starting another.")


def venv_python() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def ensure_project_venv() -> None:
    """Ensure the project virtual environment and declared PDF dependencies exist."""
    if not REQUIREMENTS.is_file():
        fail("requirements.txt is missing; cannot prepare the project environment.")

    python = venv_python()
    if not python.is_file():
        print("Project .venv not found; creating it...")
        subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], cwd=ROOT, check=True)

    if not python.is_file():
        fail(f"Project virtual environment is unavailable: {python}")

    print("Checking project .venv dependencies...")
    subprocess.run(
        [str(python), "-m", "pip", "install", "-r", str(REQUIREMENTS)],
        cwd=ROOT,
        check=True,
    )
    print(f"Project environment ready: {python}")


def _safe_filename_part(value: str) -> str:
    value = value.strip().replace("/", "-").replace("\\", "-")
    value = " ".join(value.split())
    safe = "".join(ch if ch.isalnum() or ch in " ._-()" else "-" for ch in value)
    safe = " ".join(safe.split())
    return safe.strip(" ._-") or "job"


def _aggregate_job_filename(index: int, job_text: str) -> str:
    company = ""
    role = ""
    for line in job_text.splitlines():
        stripped = line.strip()
        if not company and stripped.lower().startswith("company logo for,"):
            company = stripped.split(",", 1)[1].strip().rstrip(".")
        elif company and stripped and stripped != company and not role:
            role = stripped
    label = _safe_filename_part(company or f"Job {index:02d}")
    if role:
        label = f"{label}_{_safe_filename_part(role)}"
    return f"{index:02d}_{label}.txt"


def materialize_aggregate_vacancies() -> None:
    aggregate = INBOX / AGGREGATE_INPUT
    if not aggregate.is_file():
        return

    text = aggregate.read_text(encoding="utf-8")
    jobs = [part.strip() for part in text.split(JOB_DELIMITER) if part.strip()]
    if not jobs:
        fail(f"{AGGREGATE_INPUT} contains no jobs separated by {JOB_DELIMITER!r}.")

    for index, job_text in enumerate(jobs, 1):
        filename = _aggregate_job_filename(index, job_text)
        destination = INBOX / filename
        content = job_text.rstrip() + "\n"
        if destination.exists():
            if destination.read_text(encoding="utf-8") != content:
                fail(
                    f"Generated vacancy file already exists with different content: {filename}. "
                    f"Rename/remove the conflicting file before prepare."
                )
        else:
            destination.write_text(content, encoding="utf-8")

    print(f"Parsed {len(jobs)} vacancies from {AGGREGATE_INPUT} using {JOB_DELIMITER!r}.")


def prepare() -> None:
    ensure_no_active_batch()
    ensure_project_venv()
    INBOX.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    BATCH.mkdir(parents=True, exist_ok=True)
    RECORDS.mkdir(parents=True, exist_ok=True)

    materialize_aggregate_vacancies()

    files = sorted(
        (p for p in INBOX.iterdir() if p.is_file() and p.suffix.lower() == ".txt" and p.name.casefold() != AGGREGATE_INPUT),
        key=lambda p: p.name.casefold(),
    )
    selected = files[:MAX_FILES]
    if not selected:
        fail("No .txt job postings found in inbox/. Put job files there or add vacancies.txt with ---JOB--- separators.")

    batch_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    manifest = {
        "schema": 1,
        "batch_id": batch_id,
        "created_at": now(),
        "max_files": MAX_FILES,
        "rule_hashes": rules_snapshot(),
        "files": [
            {
                "name": p.name,
                "source_sha256": sha256(p),
                "status": "in_progress" if i == 0 else "pending",
            }
            for i, p in enumerate(selected)
        ],
    }
    atomic_write(MANIFEST, manifest)
    LOCK.write_text(batch_id + "\n", encoding="utf-8")

    print(f"Batch {batch_id}")
    for i, item in enumerate(manifest["files"], 1):
        marker = "CURRENT" if item["status"] == "in_progress" else "pending"
        print(f"{i}. {item['name']} [{marker}]")
    remaining = len(files) - len(selected)
    if remaining:
        print(f"Remaining in inbox for later batches: {remaining}")


def current() -> None:
    manifest = load_manifest()
    verify_rules(manifest)
    current_items = [x for x in manifest["files"] if x["status"] == "in_progress"]
    if not current_items:
        fail("Batch has no current job.")
    item = current_items[0]
    source = INBOX / item["name"]
    if not source.is_file():
        fail(f"Current job is missing from inbox/: {item['name']}")
    if sha256(source) != item["source_sha256"]:
        fail(f"Current job changed since batch preparation: {item['name']}")
    print(item["name"])


def list_batch() -> None:
    manifest = load_manifest()
    verify_rules(manifest)
    print(f"Batch {manifest['batch_id']}")
    for i, item in enumerate(manifest["files"], 1):
        print(f"{i}. {item['name']} [{item['status']}]")


def complete(filename: str, record_file: str | None) -> None:
    manifest = load_manifest()
    verify_rules(manifest)

    items = manifest["files"]
    current_items = [x for x in items if x["status"] == "in_progress"]
    if not current_items:
        fail("There is no current job to complete.")
    current_item = current_items[0]
    if filename != current_item["name"]:
        fail(f"Only the current job may be completed: {current_item['name']}")

    source = INBOX / filename
    if not source.is_file():
        fail(f"Source file not found: {source}")
    if sha256(source) != current_item["source_sha256"]:
        fail(f"Source file changed during processing: {filename}")

    if record_file:
        record = Path(record_file)
        if not record.is_absolute():
            record = ROOT / record
        if not record.is_file():
            fail(f"Execution record not found: {record}")
        if len(record.read_text(encoding="utf-8").strip()) == 0:
            fail("Execution record is empty.")
    else:
        fail("A temporary execution record is required. Pass its path as the second argument.")

    PROCESSED.mkdir(parents=True, exist_ok=True)
    destination = PROCESSED / filename
    if destination.exists():
        # Filenames can legitimately repeat across batches. Preserve the
        # previous processed file and give this batch a collision-safe name.
        destination = PROCESSED / f'{manifest["batch_id"]}__{filename}'

    OUTPUT.mkdir(parents=True, exist_ok=True)
    log = OUTPUT / "execution_log.md"
    record_text = Path(record_file if Path(record_file).is_absolute() else ROOT / record_file).read_text(encoding="utf-8").rstrip() + "\n\n"
    with log.open("a", encoding="utf-8") as f:
        f.write(record_text)

    shutil.move(str(source), str(destination))
    current_item["status"] = "done"
    current_item["completed_at"] = now()

    pending = [x for x in items if x["status"] == "pending"]
    if pending:
        pending[0]["status"] = "in_progress"
    atomic_write(MANIFEST, manifest)

    print(f"Completed: {filename}")
    if pending:
        print(f"Next: {pending[0]['name']}")
    else:
        MANIFEST.unlink(missing_ok=True)
        LOCK.unlink(missing_ok=True)
        print("Batch complete.")


def abort() -> None:
    manifest = load_manifest()
    print(f"Aborting batch {manifest['batch_id']}; no inbox files will be moved.")
    MANIFEST.unlink(missing_ok=True)
    LOCK.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Deterministic inbox batch controller")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("prepare")
    sub.add_parser("current")
    sub.add_parser("list")
    p = sub.add_parser("complete")
    p.add_argument("filename")
    p.add_argument("record_file")
    sub.add_parser("abort")
    args = parser.parse_args()

    {
        "prepare": prepare,
        "current": current,
        "list": list_batch,
        "complete": lambda: complete(args.filename, args.record_file),
        "abort": abort,
    }[args.command]()


if __name__ == "__main__":
    main()
