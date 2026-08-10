#!/usr/bin/env python3
"""Focused regressions for the Project Status v2 template consumer."""

from __future__ import annotations

import copy
import unittest

from project_status_v2 import (
    AUTHORITY,
    REQUIRED_ENVIRONMENTS,
    STAGES,
    StatusError,
    derive_verified,
    initial_record,
    validate,
)


class ProjectStatusV2Tests(unittest.TestCase):
    def test_initial_record_is_insufficient_and_complete_in_shape(self) -> None:
        record = initial_record("owner/example", "Example")
        self.assertEqual(record["percentage_complete"]["estimate"], 0)
        self.assertEqual(record["lifecycle_status"]["authority"], AUTHORITY)
        self.assertEqual(record["lifecycle_status"]["verified"], "insufficient")
        self.assertEqual(
            [item["stage"] for item in record["lifecycle_status"]["stages"]],
            list(STAGES),
        )
        self.assertTrue(
            all(
                item["result"] == "INSUFFICIENT"
                for item in record["lifecycle_status"]["stages"]
            )
        )
        validate(record)

    def test_percentage_cannot_create_completion(self) -> None:
        record = initial_record("owner/example", "Example")
        record["percentage_complete"]["estimate"] = 100
        record["lifecycle_status"]["claimed"] = "complete"
        self.assertEqual(derive_verified(record), "insufficient")
        with self.assertRaises(StatusError):
            record["lifecycle_status"]["verified"] = "complete"
            validate(record)

    def test_proxy_pass_is_rejected(self) -> None:
        record = initial_record("owner/example", "Example")
        designed = record["lifecycle_status"]["stages"][0]
        designed.update(
            {
                "result": "PASS",
                "relationship": "proxy",
                "observed_environment": REQUIRED_ENVIRONMENTS["designed"],
                "evidence": ["fixture:proxy"],
            }
        )
        with self.assertRaises(StatusError):
            validate(record)

    def test_complete_requires_direct_evidence_for_every_required_stage(self) -> None:
        record = initial_record("owner/example", "Example")
        record["lifecycle_status"]["claimed"] = "complete"
        for item in record["lifecycle_status"]["stages"]:
            stage = item["stage"]
            item.update(
                {
                    "result": "PASS",
                    "relationship": "direct",
                    "observed_environment": REQUIRED_ENVIRONMENTS[stage],
                    "evidence": [f"evidence:{stage}"],
                    "limitations": [],
                }
            )
        record["lifecycle_status"]["verified"] = "complete"
        validate(record)

        missing = copy.deepcopy(record)
        missing["lifecycle_status"]["stages"][-1].update(
            {
                "result": "INSUFFICIENT",
                "relationship": "missing",
                "evidence": [],
            }
        )
        missing["lifecycle_status"]["stages"][-1].pop("observed_environment", None)
        missing["lifecycle_status"]["verified"] = "insufficient"
        validate(missing)
        self.assertEqual(derive_verified(missing), "insufficient")


if __name__ == "__main__":
    unittest.main()
