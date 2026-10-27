import copy
import unittest

from scripts.readiness import assess


def good():
    rows = [{"reference": "pinned-reference", "rank_correlation": 0.5, "overlap_3px": 0.6}]
    return {
        "lane": "assigned-method",
        "template_commit": "pinned-template-commit",
        "metric": {
            "alpha": 0.2,
            "beta": 0.8,
            "kernel_radius_m": 300,
            "kernel": "triangular",
        },
        "holdout": {
            "evaluator_version": "shared-v1",
            "withheld_positives": 100,
            "dti": 0.20,
            "ci95": [0.16, 0.24],
            "paired_delta_ci95": [0.005, 0.02],
        },
        "baseline_holdout_dti": 0.19,
        "hide_recover_protocol_verified": True,
        "feature_auc": {"magnetic": 0.7, "terrain": 0.82},
        "registry": {
            "coverage_complete": True,
            "snapshot_sha256": "a" * 64,
            "surface": rows,
            "final_dots": copy.deepcopy(rows),
        },
        "validator": {
            key: True
            for key in (
                "single_band",
                "finite_inside",
                "range_0_1",
                "crs_match",
                "shape_match",
                "transform_match",
                "outside_nodata",
            )
        },
        "raster_sha256": "b" * 64,
        "submission_name": "unique-method",
        "submission_note": "Research candidate",
    }


class GateTests(unittest.TestCase):
    def test_empty_and_non_object_fail_closed(self):
        self.assertEqual(assess({})["verdict"], "negative")
        self.assertEqual(assess(None)["verdict"], "negative")
        self.assertEqual(assess([])["verdict"], "negative")

    def test_complete_evidence_passes_but_never_authorizes_slot(self):
        self.assertEqual(
            assess(good()),
            {"verdict": "promote", "reasons": [], "slot_authorized": False},
        )

    def test_each_required_top_level_section_is_mandatory(self):
        for key in good():
            with self.subTest(key=key):
                card = good()
                del card[key]
                self.assertEqual(assess(card)["verdict"], "negative")

    def test_wrong_metric_configuration_fails(self):
        for key, value in (("alpha", 0.5), ("beta", 0.2), ("kernel_radius_m", 200), ("kernel", "gaussian")):
            with self.subTest(key=key):
                card = good()
                card["metric"][key] = value
                self.assertEqual(assess(card)["verdict"], "negative")

    def test_duplicate_checks_surface_and_final_dots(self):
        for stage in ("surface", "final_dots"):
            for metric, value in (("rank_correlation", 0.901), ("overlap_3px", 0.701)):
                with self.subTest(stage=stage, metric=metric):
                    card = good()
                    card["registry"][stage][0][metric] = value
                    self.assertEqual(assess(card)["verdict"], "negative")

    def test_canaries_reject_nonfinite_or_high_auc(self):
        for value in (float("nan"), float("inf"), 0.91, -0.1):
            with self.subTest(value=value):
                card = good()
                card["feature_auc"]["magnetic"] = value
                self.assertEqual(assess(card)["verdict"], "negative")

    def test_no_holdout_improvement_fails(self):
        card = good()
        card["baseline_holdout_dti"] = 0.20
        self.assertEqual(assess(card)["verdict"], "negative")

    def test_nonpositive_paired_delta_interval_fails(self):
        for interval in ([0.0, 0.02], [-0.01, 0.02], [-0.03, -0.01]):
            with self.subTest(interval=interval):
                card = good()
                card["holdout"]["paired_delta_ci95"] = interval
                self.assertEqual(assess(card)["verdict"], "negative")

    def test_malformed_nested_objects_fail_without_raising(self):
        cases = (
            {"holdout": None},
            {"feature_auc": [0.4]},
            {"registry": None},
            {"registry": {"coverage_complete": True, "snapshot_sha256": "x", "surface": [None]}},
            {"validator": None},
            {"submission_note": 7},
        )
        for change in cases:
            with self.subTest(change=change):
                card = good()
                card.update(change)
                self.assertEqual(assess(card)["verdict"], "negative")

    def test_missing_outside_nodata_fails(self):
        card = good()
        del card["validator"]["outside_nodata"]
        self.assertEqual(assess(card)["verdict"], "negative")


if __name__ == "__main__":
    unittest.main()
