#!/usr/bin/env python3
"""Focused regressions for the Project Status v2 template bootstrap consumer."""

from __future__ import annotations

import copy
import unittest

from project_status_v2 import (
    AUTHORITY,
    REQUIRED_ENVIRONMENTS,
    STAGES,
    StatusError,
    initial_record,
    validate_consumer_pointer,
    validate_initial_bootstrap,
)


class ProjectStatusV2BootstrapTests(unittest.TestCase):
    def test_initial_record_is_insufficient_and_complete_in_shape(self) -> None:
        record = initial_record("owner/example", "Example")
        self.assertEqual(record["percentage_complete"]["estimate"], 0)
        self.assertEqual(record["lifecycle_status"]["authority"], AUTHORITY)
        self.assertEqual(record["lifecycle_status"]["claimed"], "designed")
        self.assertEqual(record["lifecycle_status"]["verified"], "insufficient")
        self.assertEqual(
            [item["stage"] for item in record["lifecycle_status"]["stages"]],
            list(STAGES),
        )
        self.assertTrue(
            all(
                item["required"] is True
                and item["result"] == "INSUFFICIENT"
                and item["relationship"] == "missing"
                and item["evidence"] == []
                and item["required_environment"] == REQUIRED_ENVIRONMENTS[item["stage"]]
                for item in record["lifecycle_status"]["stages"]
            )
        )
        validate_initial_bootstrap(record)

    def test_bootstrap_rejects_percentage_inflation(self) -> None:
        record = initial_record("owner/example", "Example")
        record["percentage_complete"]["estimate"] = 100
        with self.assertRaises(StatusError):
            validate_initial_bootstrap(record)

    def test_bootstrap_rejects_proxy_or_pass_substitution(self) -> None:
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
            validate_initial_bootstrap(record)

    def test_bootstrap_rejects_stage_relaxation(self) -> None:
        record = initial_record("owner/example", "Example")
        human = record["lifecycle_status"]["stages"][-1]
        human.update(
            {
                "required": False,
                "result": "NOT_APPLICABLE",
                "relationship": "not-applicable",
                "rationale": "Attempted local relaxation.",
            }
        )
        with self.assertRaises(StatusError):
            validate_initial_bootstrap(record)

    def test_bootstrap_rejects_unsupported_completion_claim(self) -> None:
        record = initial_record("owner/example", "Example")
        record["lifecycle_status"]["claimed"] = "complete"
        record["lifecycle_status"]["verified"] = "complete"
        with self.assertRaises(StatusError):
            validate_initial_bootstrap(record)

    def test_permanent_consumer_check_does_not_reimplement_lifecycle_verdicts(self) -> None:
        record = initial_record("owner/example", "Example")
        later = copy.deepcopy(record)
        later["percentage_complete"]["estimate"] = 50
        later["lifecycle_status"]["claimed"] = "implemented"
        later["lifecycle_status"]["verified"] = "insufficient"
        later["lifecycle_status"]["stages"][0].update(
            {
                "result": "PASS",
                "relationship": "direct",
                "observed_environment": REQUIRED_ENVIRONMENTS["designed"],
                "evidence": ["project-authority:accepted"],
            }
        )
        validate_consumer_pointer(later, "owner/example")

    def test_consumer_pointer_rejects_wrong_authority_or_identity(self) -> None:
        record = initial_record("owner/example", "Example")

        wrong_authority = copy.deepcopy(record)
        wrong_authority["lifecycle_status"]["authority"] = "owner/other@deadbeef"
        with self.assertRaises(StatusError):
            validate_consumer_pointer(wrong_authority, "owner/example")

        with self.assertRaises(StatusError):
            validate_consumer_pointer(record, "owner/different")


if __name__ == "__main__":
    unittest.main()
