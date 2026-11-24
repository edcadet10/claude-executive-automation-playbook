import sqlite3
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path
from unittest.mock import Mock

from lab.queue import add_question, decide, stage, transaction
from lab.report import ENTITY, PERIOD, SAMPLE, InputError, load_snapshot


class LedgerTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.db = Path(directory.name) / "ledger.sqlite3"
        self.snapshot = load_snapshot(SAMPLE)

    def stage(self):
        return stage(self.db, self.snapshot, ENTITY, PERIOD)

    def test_concurrent_retries_share_one_id(self):
        with ThreadPoolExecutor(max_workers=4) as pool:
            runs = list(pool.map(lambda _: self.stage(), range(4)))
        self.assertEqual({draft for draft, _ in runs}, {1})
        self.assertEqual(sum(created for _, created in runs), 1)

    def test_new_source_revision_supersedes_old_pending_draft(self):
        old, _ = self.stage()
        self.snapshot["policy"]["ref"] = "POL-MARGIN-05"
        new, _ = self.stage()
        self.assertNotEqual(old, new)
        with self.assertRaisesRegex(InputError, "newer revision"):
            decide(self.db, old, "approved", "fixture reviewer", "tie-out")
        decide(self.db, new, "changes_requested", "fixture reviewer", "missing bridge")
        decide(self.db, new, "changes_requested", "fixture reviewer", "missing bridge")
        with self.assertRaises(InputError):
            decide(self.db, new, "approved", "fixture reviewer", "late edit")

    def test_model_failure_preserves_packet_and_bounds_automatic_retry(self):
        draft, _ = self.stage()
        fail = Mock(side_effect=InputError("provider unavailable"))
        for _ in range(3):
            with self.assertRaisesRegex(InputError, "provider unavailable"):
                add_question(self.db, draft, fail)
        with self.assertRaisesRegex(InputError, "Three attempts"):
            add_question(self.db, draft, fail)
        self.assertEqual(fail.call_count, 3)
        ok = Mock(return_value="Which category explains the shortfall?")
        self.assertEqual(add_question(self.db, draft, ok, manual_retry=True), "question staged")
        add_question(self.db, draft, ok)
        self.assertEqual(ok.call_count, 1)
        with transaction(self.db) as conn:
            packet, review = conn.execute("SELECT packet,review FROM drafts").fetchone()
        self.assertIn("QBO-PL-09", packet)
        self.assertEqual(review, "pending")

    def test_expired_lease_recovers_and_current_lease_blocks_second_worker(self):
        draft, _ = self.stage()
        with transaction(self.db) as conn:
            conn.execute("UPDATE drafts SET lease='interrupted', lease_until=4102444800")
        with self.assertRaisesRegex(InputError, "Another worker"):
            add_question(self.db, draft, Mock())
        with transaction(self.db) as conn:
            conn.execute("UPDATE drafts SET lease_until=0")
        self.assertEqual(add_question(self.db, draft, lambda _: "What changed?"), "question staged")

    def test_late_model_result_cannot_modify_superseded_draft(self):
        old, _ = self.stage()
        def late(_):
            self.snapshot["policy"]["ref"] = "POL-MARGIN-05"
            self.stage()
            return "What changed?"
        self.assertEqual(add_question(self.db, old, late), "superseded during drafting")
        with transaction(self.db) as conn:
            self.assertEqual(tuple(conn.execute("SELECT review,question FROM drafts WHERE id=?", (old,)).fetchone()),
                             ("superseded", None))

    def test_backup_restore_preserves_reviewer_decision_and_replay_identity(self):
        draft, _ = self.stage()
        decide(self.db, draft, "approved", "fixture reviewer", "reference reconciled")
        restored = self.db.with_name("restored.sqlite3")
        with closing(sqlite3.connect(self.db)) as source, closing(sqlite3.connect(restored)) as target:
            source.backup(target)
        self.assertEqual(stage(restored, self.snapshot, ENTITY, PERIOD), (draft, False))
        with transaction(restored) as conn:
            row = conn.execute("SELECT review,reviewer FROM drafts WHERE id=?", (draft,)).fetchone()
        self.assertEqual(tuple(row), ("approved", "fixture reviewer"))
