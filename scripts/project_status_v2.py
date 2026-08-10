#!/usr/bin/env python3
"""Generate and validate the version-pinned initial Project Status v2 record."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

AUTHORITY = "armpitpete/merrin-project-controls@7bc8b7f5ef921851ad163093f089d28d8128bf6c"
STAGES = (
    "designed",
    "implemented",
    "automated-checks",
    "independent-review",
    "merged",
    "deployed",
    "live-behaviour",
    "human-acceptance",
)
CLAIM_TO_STAGE = {
    "designed": "designed",
    "implemented": "implemented",
    "automated-checks-passed": "automated-checks",
    "independently-reviewed": "independent-review",
    "merged": "merged",
    "deployed": "deployed",
    "live-behaviour-verified": "live-behaviour",
    "human-acceptance-received": "human-acceptance",
}
REQUIRED_ENVIRONMENTS = {
    "designed": "accepted project authority",
    "implemented": "exact implementation commit",
    "automated-checks": "exact-head automated checks",
    "independent-review": "exact-head independent review",
    "merged": "default-branch commit",
    "deployed": "declared deployment environment",
    "live-behaviour": "actual live environment",
    "human-acceptance": "declared human acceptance environment",
}
FORBIDDEN_FRAGMENTS = (
    "GH_TOKEN",
    "GITHUB_TOKEN",
    "private inventory",
    "BEGIN PRIVATE KEY",
    "sk-",
)


class StatusError(ValueError):
    """Raised when a Project Status v2 consumer record is not truthful."""


def initial_record(repository: str, project_name: str) -> dict[str, Any]:
    stages = [
        {
            "stage": stage,
            "required": True,
            "required_environment": REQUIRED_ENVIRONMENTS[stage],
            "result": "INSUFFICIENT",
            "relationship": "missing",
            "evidence": [],
            "limitations": [f"No direct {stage} evidence has been recorded yet."],
        }
        for stage in STAGES
    ]
    return {
        "project": repository,
        "finish_line": f"Define and evidence the first bounded finish line for {project_name}.",
        "percentage_complete": {
            "estimate": 0,
            "confidence": "high",
            "evidence": [
                "Only repository bootstrap has occurred; project work is not counted as complete."
            ],
            "remaining_work": [
                "Accept a bounded project authority and record direct lifecycle evidence."
            ],
            "blockers": [],
        },
        "completion_likelihood": {
            "assessment": "possible",
            "confidence": "low",
            "reasons": [
                "The project has been created, but its first accepted finish line is not yet evidenced."
            ],
        },
        "lifecycle_status": {
            "claimed": "designed",
            "verified": "insufficient",
            "authority": AUTHORITY,
            "limitations": [
                "Generated bootstrap fixture; not implementation, deployment, live-behaviour or acceptance evidence."
            ],
            "stages": stages,
        },
        "next_bounded_action": (
            "Assess and inventory source material without modifying it, then accept one bounded project authority."
        ),
    }


def _stage_map(record: dict[str, Any]) -> dict[str, dict[str, Any]]:
    lifecycle = record.get("lifecycle_status")
    if not isinstance(lifecycle, dict):
        raise StatusError("lifecycle_status must be an object")
    stages = lifecycle.get("stages")
    if not isinstance(stages, list):
        raise StatusError("lifecycle_status.stages must be an array")
    if [item.get("stage") for item in stages if isinstance(item, dict)] != list(STAGES):
        raise StatusError("lifecycle_status.stages must contain all eight stages in canonical order")
    if any(not isinstance(item, dict) for item in stages):
        raise StatusError("every lifecycle stage must be an object")
    return {item["stage"]: item for item in stages}


def derive_verified(record: dict[str, Any]) -> str:
    stages = _stage_map(record)
    lifecycle = record["lifecycle_status"]
    claimed = lifecycle.get("claimed")
    valid_claims = set(CLAIM_TO_STAGE) | {"complete"}
    if claimed not in valid_claims:
        raise StatusError(f"unsupported lifecycle claim: {claimed!r}")

    required = [stage for stage in STAGES if stages[stage].get("required") is True]
    if not required:
        raise StatusError("at least one lifecycle stage must be required")

    if claimed == "complete":
        relevant = required
    else:
        claimed_stage = CLAIM_TO_STAGE[claimed]
        claim_index = STAGES.index(claimed_stage)
        relevant = [stage for stage in required if STAGES.index(stage) <= claim_index]

    for stage in relevant:
        item = stages[stage]
        result = item.get("result")
        if result == "FAIL":
            if (
                item.get("relationship") == "direct"
                and item.get("observed_environment") == item.get("required_environment")
            ):
                return "failed"
            return "insufficient"
        if not (
            result == "PASS"
            and item.get("relationship") == "direct"
            and item.get("observed_environment") == item.get("required_environment")
            and isinstance(item.get("evidence"), list)
            and len(item["evidence"]) > 0
        ):
            return "insufficient"

    return "complete" if claimed == "complete" else claimed


def validate(record: Any) -> None:
    if not isinstance(record, dict):
        raise StatusError("project status must be an object")

    required_top = {
        "project",
        "finish_line",
        "percentage_complete",
        "completion_likelihood",
        "lifecycle_status",
        "next_bounded_action",
    }
    missing = sorted(required_top - set(record))
    if missing:
        raise StatusError("missing fields: " + ", ".join(missing))

    percentage = record.get("percentage_complete")
    if not isinstance(percentage, dict):
        raise StatusError("percentage_complete must be an object")
    estimate = percentage.get("estimate")
    if not isinstance(estimate, int) or isinstance(estimate, bool) or not 0 <= estimate <= 100:
        raise StatusError("percentage_complete.estimate must be an integer from 0 to 100")

    stages = _stage_map(record)
    lifecycle = record["lifecycle_status"]
    if lifecycle.get("authority") != AUTHORITY:
        raise StatusError("lifecycle authority must match the exact shared Project Status v2 pin")

    for stage in STAGES:
        item = stages[stage]
        required = item.get("required")
        result = item.get("result")
        relationship = item.get("relationship")
        evidence = item.get("evidence")
        if required is True:
            if item.get("required_environment") != REQUIRED_ENVIRONMENTS[stage]:
                raise StatusError(f"{stage}: required_environment does not match the local consumer contract")
            if result not in {"PASS", "FAIL", "INSUFFICIENT"}:
                raise StatusError(f"{stage}: required stage has invalid result {result!r}")
            if relationship not in {"direct", "proxy", "missing"}:
                raise StatusError(f"{stage}: invalid evidence relationship {relationship!r}")
            if not isinstance(evidence, list):
                raise StatusError(f"{stage}: evidence must be an array")
            if result in {"PASS", "FAIL"} and relationship != "direct":
                raise StatusError(f"{stage}: PASS/FAIL requires direct evidence")
            if result in {"PASS", "FAIL"} and item.get("observed_environment") != item.get("required_environment"):
                raise StatusError(f"{stage}: PASS/FAIL requires the declared real environment")
            if result in {"PASS", "FAIL"} and not evidence:
                raise StatusError(f"{stage}: PASS/FAIL requires evidence")
        elif required is False:
            if result != "NOT_APPLICABLE" or relationship != "not-applicable":
                raise StatusError(f"{stage}: non-required stage must be NOT_APPLICABLE")
            if not isinstance(item.get("rationale"), str) or not item["rationale"].strip():
                raise StatusError(f"{stage}: non-required stage requires a rationale")
        else:
            raise StatusError(f"{stage}: required must be boolean")

    expected = derive_verified(record)
    if lifecycle.get("verified") != expected:
        raise StatusError(
            f"verified lifecycle status {lifecycle.get('verified')!r} does not match evidence-derived {expected!r}"
        )

    rendered = json.dumps(record, sort_keys=True)
    for fragment in FORBIDDEN_FRAGMENTS:
        if fragment.lower() in rendered.lower():
            raise StatusError(f"project status contains forbidden private/control-plane fragment: {fragment}")


def write_initial_record(path: Path, repository: str, project_name: str) -> None:
    record = initial_record(repository, project_name)
    validate(record)
    path.write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def load_and_validate(path: Path) -> None:
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise StatusError(f"cannot read project status: {exc}") from exc
    validate(record)
