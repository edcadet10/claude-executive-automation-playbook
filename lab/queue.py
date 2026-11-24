"""Stage financial drafts in a durable, single-entity review ledger."""
import argparse
import hashlib
import json
import sqlite3
import subprocess
import sys
import time
import uuid
from contextlib import contextmanager
from pathlib import Path

from lab.report import ENTITY, PERIOD, SAMPLE, build_packet, load_snapshot, require

SCHEMA = """
CREATE TABLE IF NOT EXISTS drafts (
    id INTEGER PRIMARY KEY, entity TEXT NOT NULL, period TEXT NOT NULL, revision TEXT NOT NULL,
    packet TEXT NOT NULL, review TEXT NOT NULL DEFAULT 'pending', reviewer TEXT, note TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, reviewed_at TEXT,
    question TEXT, attempts INTEGER NOT NULL DEFAULT 0, lease TEXT, lease_until INTEGER,
    UNIQUE(entity, period, revision)
)
"""


@contextmanager
def transaction(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=20, isolation_level=None)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(SCHEMA)
        yield connection
        connection.commit()
    except BaseException:
        connection.rollback()
        raise
    finally:
        connection.close()


def stage(db, snapshot, entity, period):
    packet = build_packet(snapshot, entity, period)
    canonical = json.dumps(snapshot, sort_keys=True, separators=(",", ":"))
    revision = hashlib.sha256(canonical.encode()).hexdigest()
    with transaction(db) as conn:
        existing = conn.execute("SELECT id FROM drafts WHERE entity=? AND period=? AND revision=?",
                                (entity, period, revision)).fetchone()
        if existing:
            return existing["id"], False
        conn.execute("UPDATE drafts SET review='superseded', lease=NULL, lease_until=NULL "
                     "WHERE entity=? AND period=? AND review='pending'", (entity, period))
        cursor = conn.execute("INSERT INTO drafts(entity,period,revision,packet) VALUES(?,?,?,?)",
                              (entity, period, revision, json.dumps(packet)))
        return cursor.lastrowid, True


def get_draft(conn, draft_id):
    row = conn.execute("SELECT * FROM drafts WHERE id=?", (draft_id,)).fetchone()
    require(row is not None, "Unknown draft ID")
    return row


def decide(db, draft_id, decision, reviewer, note):
    require(decision in ("approved", "changes_requested"), "Unknown decision")
    require(bool(reviewer.strip()) and bool(note.strip()), "Record the reviewer and their finding")
    with transaction(db) as conn:
        row = get_draft(conn, draft_id)
        if (row["review"], row["reviewer"], row["note"]) == (decision, reviewer, note):
            return
        require(row["review"] == "pending", "This draft already has a decision or a newer revision")
        require(not row["lease"] or row["lease_until"] <= time.time(), "Draft question in progress")
        conn.execute("UPDATE drafts SET review=?,reviewer=?,note=?,reviewed_at=CURRENT_TIMESTAMP,"
                     "lease=NULL,lease_until=NULL WHERE id=?", (decision, reviewer, note, draft_id))


def ask_claude(packet):
    prompt = ("Write one short question the controller can investigate about this month-end variance. "
              "Use the evidence below, keep causes open, and return only a single question.\n"
              + json.dumps(packet, sort_keys=True))
    command = ["claude", "-p", "--bare", "--model", "haiku", "--tools", "",
               "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}', "--no-session-persistence",
               "--permission-mode", "dontAsk", "--max-budget-usd", "0.25", "--output-format", "json"]
    run = subprocess.run(command, input=prompt, capture_output=True, encoding="utf-8",
                         errors="replace", timeout=120, check=False)
    require(run.returncode == 0, "Model call failed; verified packet retained for review")
    reply = json.loads(run.stdout)
    require(isinstance(reply, dict) and not reply.get("is_error"), "Incomplete model response")
    question = reply.get("result")
    require(isinstance(question, str) and 5 <= len(question.strip()) <= 350
            and question.strip().endswith("?"), "Model response needs human review")
    return question.strip()


def add_question(db, draft_id, generate=ask_claude, *, manual_retry=False):
    token = uuid.uuid4().hex
    now = int(time.time())
    with transaction(db) as conn:
        row = get_draft(conn, draft_id)
        if row["question"] or row["review"] != "pending":
            return "already completed or superseded"
        require(not row["lease"] or row["lease_until"] <= now, "Another worker is drafting")
        require(row["attempts"] < 3 or manual_retry, "Three attempts used; operator review required")
        conn.execute("UPDATE drafts SET lease=?,lease_until=?,attempts=attempts+1 WHERE id=?",
                     (token, now + 180, draft_id))
        packet = json.loads(row["packet"])
    try:
        question = generate(packet)
    except Exception:
        with transaction(db) as conn:
            conn.execute("UPDATE drafts SET lease=NULL,lease_until=NULL WHERE id=? AND lease=?",
                         (draft_id, token))
        raise
    with transaction(db) as conn:
        cursor = conn.execute("UPDATE drafts SET question=?,lease=NULL,lease_until=NULL "
                              "WHERE id=? AND lease=? AND review='pending'", (question, draft_id, token))
        return "question staged" if cursor.rowcount else "superseded during drafting"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=Path(".runtime/fieldbook.sqlite3"))
    commands = parser.add_subparsers(dest="command", required=True)
    job = commands.add_parser("stage")
    job.add_argument("--input", type=Path, default=SAMPLE)
    job.add_argument("--entity", default=ENTITY)
    job.add_argument("--period", default=PERIOD)
    job.add_argument("--with-claude", action="store_true")
    show = commands.add_parser("show")
    show.add_argument("id", type=int)
    decision = commands.add_parser("review")
    decision.add_argument("id", type=int)
    decision.add_argument("--decision", required=True, choices=["approved", "changes_requested"])
    decision.add_argument("--reviewer", required=True)
    decision.add_argument("--note", required=True)
    retry = commands.add_parser("retry-question")
    retry.add_argument("id", type=int)
    args = parser.parse_args()
    try:
        if args.command == "stage":
            draft_id, created = stage(args.db, load_snapshot(args.input), args.entity, args.period)
            print(json.dumps({"draft_id": draft_id, "created": created}), flush=True)
            if args.with_claude:
                print(add_question(args.db, draft_id))
        elif args.command == "review":
            decide(args.db, args.id, args.decision, args.reviewer, args.note)
            print("Decision recorded.")
        elif args.command == "retry-question":
            print(add_question(args.db, args.id, manual_retry=True))
        else:
            with transaction(args.db) as conn:
                row = dict(get_draft(conn, args.id))
            row.pop("lease")
            row["packet"] = json.loads(row["packet"])
            print(json.dumps(row, indent=2))
    except (ValueError, OSError, sqlite3.Error, subprocess.TimeoutExpired) as exc:
        if isinstance(exc, subprocess.TimeoutExpired):
            print("Held: model timed out; verified packet retained.", file=sys.stderr)
        else:
            print(f"Held: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
