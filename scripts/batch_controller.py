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


def prepare() -> None:
    ensure_no_active_batch()
    INBOX.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    BATCH.mkdir(parents=True, exist_ok=True)
    RECORDS.mkdir(parents=True, exist_ok=True)

    files = sorted(
        (p for p in INBOX.iterdir() if p.is_file() and p.suffix.lower() == ".txt"),
        key=lambda p: p.name.casefold(),
    )
    selected = files[:MAX_FILES]
    if not selected:
        fail("No .txt job postings found in inbox/.")

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
