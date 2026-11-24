import unittest

from lab.report import ENTITY, PERIOD, SAMPLE, InputError, build_packet, load_snapshot


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.inputs = load_snapshot(SAMPLE)

    def packet(self):
        return build_packet(self.inputs, ENTITY, PERIOD)

    def test_controller_reference(self):
        packet = self.packet()
        self.assertEqual(packet["gross_profit_cents"], 4250000)
        self.assertEqual(packet["open_pipeline_cents"], 6000000)
        self.assertEqual(packet["gross_margin_pct"], "17.00")
        self.assertEqual(packet["variance_percentage_points"], "-1.00")
        self.assertEqual(packet["profit_variance_usd"], "-2500.00")
        self.assertEqual(packet["threshold_result"], "below_floor")
        self.assertEqual(set(packet["sources"].values()), {"CRM-SNAPSHOT-09", "QBO-PL-09", "POL-MARGIN-04"})

    def test_each_foreign_source_is_held(self):
        for source in ("crm", "pl", "policy"):
            with self.subTest(source=source):
                inputs = load_snapshot(SAMPLE)
                inputs[source]["entity"] = "south-store"
                with self.assertRaisesRegex(InputError, "Entity mismatch"):
                    build_packet(inputs, ENTITY, PERIOD)

    def test_rejects_stale_incomplete_or_inconsistent_sources(self):
        cases = [("crm", "as_of", "2026-09-29"), ("crm", "currency", "CAD"),
                 ("pl", "period", "2026-08"), ("pl", "closed", False),
                 ("pl", "basis", "cash"), ("pl", "gross_profit_cents", 0),
                 ("pl", "income_cents", 0), ("policy", "effective_from", "2026-09-02"),
                 ("policy", "floor_bps", True)]
        for section, key, value in cases:
            with self.subTest(key=key):
                inputs = load_snapshot(SAMPLE)
                inputs[section][key] = value
                with self.assertRaises(InputError):
                    build_packet(inputs, ENTITY, PERIOD)

    def test_empty_pipeline_is_valid_and_independent_of_margin(self):
        self.inputs["crm"]["open_deals"] = []
        packet = self.packet()
        self.assertEqual((packet["open_deal_count"], packet["gross_margin_pct"]), (0, "17.00"))

    def test_duplicate_deal_is_held(self):
        self.inputs["crm"]["open_deals"] *= 2
        with self.assertRaisesRegex(InputError, "Duplicate deal"):
            self.packet()

    def test_floor_decision_uses_full_precision(self):
        self.inputs["pl"].update(cogs_cents=20500001, gross_profit_cents=4499999)
        packet = self.packet()
        self.assertEqual(packet["gross_margin_pct"], "18.00")
        self.assertEqual(packet["threshold_result"], "below_floor")
        self.assertEqual(packet["profit_variance_usd"], "-0.01")
